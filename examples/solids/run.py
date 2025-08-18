"""
Main module for running the API
"""
import uvicorn
from g4f import version
from g4f.client.helper import filter_none

from .config import AppConfig, DEFAULT_PORT
from .app import (
    create_app as _create_app, 
    create_app_debug as _create_app_debug,
    create_app_with_gui_and_debug as _create_app_with_gui_and_debug, 
    create_app_with_demo_and_debug as _create_app_with_demo_and_debug
)

def run_api(
    host: str = '0.0.0.0',
    port: int = None,
    bind: str = None,
    debug: bool = False,
    use_colors: bool = None,
    **kwargs
) -> None:
    print(f'Starting server... [g4f v-{version.utils.current_version}]' + (" (debug)" if debug else ""))
    
    if use_colors is None:
        use_colors = debug
    
    if bind is not None:
        host, port = bind.split(":")
    
    if port is None:
        port = DEFAULT_PORT
    
    if AppConfig.demo and debug:
        method = "create_app_with_demo_and_debug"
    elif AppConfig.gui and debug:
        method = "create_app_with_gui_and_debug"
    else:
        method = "create_app_debug" if debug else "create_app"
    
    uvicorn.run(
        f"examples.custom_inference_api:{method}",
        host=host,
        port=int(port),
        factory=True,
        use_colors=use_colors,
        **filter_none(**kwargs)
    )