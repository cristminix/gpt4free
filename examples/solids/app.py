"""
App creation and setup module
"""
import g4f
import g4f.debug
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from a2wsgi import WSGIMiddleware
    has_a2wsgi = True
except ImportError:
    has_a2wsgi = False

from g4f.gui import get_gui_app
from g4f import Provider
from g4f.errors import MissingRequirementsError

from .config import AppConfig
from .utils import lifespan
from .api.core import Api

def create_app():
    app = FastAPI(lifespan=lifespan)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    api = Api(app)

    api.register_routes()
    api.register_authorization()
    api.register_validation_exception_handler()

    if AppConfig.gui:
        if not has_a2wsgi:
            raise MissingRequirementsError("a2wsgi is required for GUI. Install it with: pip install a2wsgi")
        gui_app = WSGIMiddleware(get_gui_app(AppConfig.demo, AppConfig.timeout))
        app.mount("/", gui_app)

    if AppConfig.ignored_providers:
        for provider in AppConfig.ignored_providers:
            if provider in Provider.__map__:
                Provider.__map__[provider].working = False

    return app

def create_app_debug():
    g4f.debug.logging = True
    return create_app()

def create_app_with_gui_and_debug():
    g4f.debug.logging = True
    AppConfig.gui = True
    return create_app()

def create_app_with_demo_and_debug():
    g4f.debug.logging = True
    AppConfig.gui = True
    AppConfig.demo = True
    return create_app()