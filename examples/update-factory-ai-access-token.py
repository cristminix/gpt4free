#!/usr/bin/env python3
"""
Script to get access token from WorkOS API using refresh token.
"""

import os
import re
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from urllib.parse import urlencode


class TokenResponse:
    """Response from WorkOS token authentication."""
    
    def __init__(self, data: Dict[str, Any]):
        self.access_token: str = data.get("access_token", "")
        self.refresh_token: str = data.get("refresh_token", "")
        self.token_type: str = data.get("token_type", "")
        self.expires_in: int = data.get("expires_in", 0)
        self.raw_data: Dict[str, Any] = data
    
    def __repr__(self) -> str:
        return f"TokenResponse(access_token={self.access_token[:20]}..., expires_in={self.expires_in})"


def get_access_token(
    refresh_token: str,
    client_id: str = "client_01HNM792M5G5G1A2THWPXKFMXB"
) -> TokenResponse:
    """
    Get access token from WorkOS API using refresh token.
    
    Args:
        refresh_token: The refresh token to use for authentication
        client_id: The client ID (default: "client_01HNM792M5G5G1A2THWPXKFMXB")
    
    Returns:
        TokenResponse object containing the access token and other auth data
    
    Raises:
        requests.exceptions.RequestException: If the HTTP request fails
        Exception: For other errors during token retrieval
    """
    url = "https://api.workos.com/user_management/authenticate"
    
    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }
    # print({"body": body})
    
    try:
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Bun/1.2.23",
            },
            data=urlencode(body),
            timeout=30
        )
        
        if not response.ok:
            raise Exception(f"HTTP error! status: {response.status_code}")
        
        data = response.json()
        return TokenResponse(data)
    
    except requests.exceptions.RequestException as error:
        print(f"Error getting access token: {error}")
        raise
    except Exception as error:
        print(f"Error getting access token: {error}")
        raise

def update_access_token_env() -> None:
    """
    Update FACTORY_AI_TOKEN and FACTORY_AI_REFRESH_TOKEN in .env file.
    
    This function:
    1. Reads FACTORY_AI_REFRESH_TOKEN from environment
    2. Gets a new access token from WorkOS API
    3. Updates both tokens in the .env file
    
    Raises:
        Exception: If token retrieval or file update fails
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Get a new access token
        refresh_token = os.getenv("FACTORY_AI_REFRESH_TOKEN", "")
        
        if not refresh_token:
            raise ValueError("FACTORY_AI_REFRESH_TOKEN environment variable not set")
        
        token_response = get_access_token(refresh_token)
        
        # Read the .env file
        env_path = Path.cwd() / ".env"
        
        if not env_path.exists():
            raise FileNotFoundError(f".env file not found at {env_path}")
        
        env_content = env_path.read_text(encoding="utf-8")
        
        # Update the FACTORY_AI_TOKEN line
        updated_content = re.sub(
            r'^FACTORY_AI_TOKEN=.*$',
            f'FACTORY_AI_TOKEN="{token_response.access_token}"',
            env_content,
            flags=re.MULTILINE
        )
        
        # Update the FACTORY_AI_REFRESH_TOKEN line
        updated_content = re.sub(
            r'^FACTORY_AI_REFRESH_TOKEN=.*$',
            f'FACTORY_AI_REFRESH_TOKEN="{token_response.refresh_token}"',
            updated_content,
            flags=re.MULTILINE
        )
        
        # Write the updated content back to the .env file
        env_path.write_text(updated_content, encoding="utf-8")
        
        print("Successfully updated FACTORY_AI_TOKEN and FACTORY_AI_REFRESH_TOKEN in .env file")
        
    except Exception as error:
        print(f"Error updating access token in .env file: {error}")
        raise


def main() -> None:
    """
    Main function to update access token in .env file.
    
    This is the entry point when the script is run directly.
    """
    try:
        update_access_token_env()
    except Exception as error:
        print(f"Error in main execution: {error}")
        exit(1)


if __name__ == "__main__":
    main()