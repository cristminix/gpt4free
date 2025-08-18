"""
Core API class
"""
import logging
import os
import secrets
import json
import time

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPBasic
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException
from starlette.status import (
    HTTP_200_OK,
    HTTP_422_UNPROCESSABLE_ENTITY, 
    HTTP_404_NOT_FOUND,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from g4f.client import AsyncClient
from g4f.providers.response import BaseConversation
from g4f.cookies import read_cookie_files, get_cookies_dir
from g4f import debug

try:
    from nodriver import util
    has_nodriver = True
except ImportError:
    has_nodriver = False

try:
    from g4f.gui.server.crypto import create_or_read_keys, decrypt_data, get_session_key
    has_crypto = True
except ImportError:
    has_crypto = False

from ..config import AppConfig
from ..utils import update_headers
from .base import ErrorResponse

logger = logging.getLogger(__name__)

class Api:
    def __init__(self, app: FastAPI) -> None:
        self.app = app
        self.client = AsyncClient()
        self.get_g4f_api_key = APIKeyHeader(name="g4f-api-key")
        self.conversations: dict[str, dict[str, BaseConversation]] = {}

    security = HTTPBearer(auto_error=False)
    basic_security = HTTPBasic()

    async def get_username(self, request: Request) -> str:
        credentials = await self.basic_security(request)
        current_password_bytes = credentials.password.encode()
        is_correct_password = secrets.compare_digest(
            current_password_bytes, AppConfig.g4f_api_key.encode()
        )
        if not is_correct_password:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username

    def register_authorization(self):
        if AppConfig.g4f_api_key:
            print(f"Register authentication key: {''.join(['*' for _ in range(len(AppConfig.g4f_api_key))])}")
        if has_crypto:
            private_key, _ = create_or_read_keys()
            session_key = get_session_key()
        @self.app.middleware("http")
        async def authorization(request: Request, call_next):
            user = None
            if request.method != "OPTIONS" and AppConfig.g4f_api_key is not None or AppConfig.demo:
                try:
                    user_g4f_api_key = await self.get_g4f_api_key(request)
                except HTTPException:
                    user_g4f_api_key = await self.security(request)
                    if hasattr(user_g4f_api_key, "credentials"):
                        user_g4f_api_key = user_g4f_api_key.credentials
                if AppConfig.g4f_api_key is None or not user_g4f_api_key or not secrets.compare_digest(AppConfig.g4f_api_key, user_g4f_api_key):
                    if has_crypto and user_g4f_api_key:
                        try:
                            expires, user = decrypt_data(private_key, user_g4f_api_key).split(":", 1)
                        except:
                            try:
                                data = json.loads(decrypt_data(session_key, user_g4f_api_key))
                                expires = int(decrypt_data(private_key, data["data"])) + 86400
                                user = data.get("user", user)
                            except:
                                return ErrorResponse.from_message(f"Invalid G4F API key", HTTP_401_UNAUTHORIZED)
                        expires = int(expires) - int(time.time())
                        debug.log(f"User: '{user}' G4F API key expires in {expires} seconds")
                        if expires < 0:
                            return ErrorResponse.from_message("G4F API key expired", HTTP_401_UNAUTHORIZED)
                else:
                    user = "admin"
                path = request.url.path
                if path.startswith("/v1") or path.startswith("/api/") or (AppConfig.demo and path == '/backend-api/v2/upload_cookies'):
                    if request.method != "OPTIONS":
                        if user_g4f_api_key is None:
                            return ErrorResponse.from_message("G4F API key required", HTTP_401_UNAUTHORIZED)
                        if AppConfig.g4f_api_key is None and user is None:
                            return ErrorResponse.from_message("Invalid G4F API key", HTTP_403_FORBIDDEN)
                elif not AppConfig.demo and not path.startswith("/images/") and not path.startswith("/media/"):
                    if user_g4f_api_key is not None:
                        if user is None:
                            return ErrorResponse.from_message("Invalid G4F API key", HTTP_403_FORBIDDEN)
                    elif path.startswith("/backend-api/") or path.startswith("/chat/") and path != "/chat/":
                        try:
                            user = await self.get_username(request)
                        except HTTPException as e:
                            return ErrorResponse.from_message(e.detail, e.status_code, e.headers)
                if user is None:
                    ip = request.headers.get("X-Forwarded-For", "")[:4].strip(":.")
                    country = request.headers.get("Cf-Ipcountry", "")
                    user = request.headers.get("x-user", ip)
                    user = f"{country}:{user}" if country else user
                request = update_headers(request, user)
            response = await call_next(request)
            return response

    def register_validation_exception_handler(self):
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            details = exc.errors()
            modified_details = []
            for error in details:
                modified_details.append({
                    "loc": error["loc"],
                    "message": error["msg"],
                    "type": error["type"],
                })
            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content=jsonable_encoder({"detail": modified_details}),
            )

    def register_routes(self):
        """Register all API routes"""
        # Import here to avoid circular imports
        from .routes import register_routes
        register_routes(self)