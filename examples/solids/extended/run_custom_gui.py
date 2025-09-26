"""
Custom web interface to run the GUI with extended providers.
"""
import sys
from pathlib import Path

# Add the root directory to the Python path so we can import g4f modules
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

def get_custom_gui_app(demo: bool = False, timeout: int = None):
    """
    Create a Flask app with custom backend API support.
    """
    from flask import Flask
    from g4f.gui.server.app import create_app
    from examples.solids.extended.website import Website
    from examples.solids.extended.custom_backend_api import CustomBackend_Api
    
    app = create_app()
    app.demo = demo
    app.timeout = timeout

    # Initialize website
    site = Website(app)
   

    # Initialize custom backend API instead of the original one
    # The CustomBackend_Api automatically registers its routes via decorators
    backend_api = CustomBackend_Api(app)
    
    # Register website routes
    for route in site.routes:
        app.add_url_rule(
            route,
            view_func=site.routes[route]['function'],
            methods=site.routes[route]['methods'],
        )
    return app

def run_gui(host: str = '0.0.0.0', port: int = 8080, debug: bool = False, demo: bool = False) -> None:
    """
    Run the GUI with extended provider support.
    
    Args:
        host (str): Host to run the server on
        port (int): Port to run the server on
        debug (bool): Enable debug mode
        demo (bool): Enable demo mode
    """
    # Import here to ensure the path is set correctly
    from flask import Flask
    from g4f import debug as g4f_debug
    
    # Enable debug logging if debug mode is enabled
    if debug:
        g4f_debug.enable_logging()
    
    config = {
        'host': host,
        'port': port,
        'debug': debug
    }

    app = get_custom_gui_app(demo=demo)
    
    print(f"Running on port {config['port']} (http://{host}:{port}/)")
    print("You can now select 'ExtendedLMArenaBeta' as a provider in the GUI")
    if __name__ != "__main__":  # When run with uvicorn
        # For uvicorn compatibility, wrap Flask app with WSGIMiddleware
        from starlette.middleware.wsgi import WSGIMiddleware
        globals()["app"] = WSGIMiddleware(app)
    else:  # When run directly
        app.run(**config)
    print(f"Closing port {config['port']}")

# Create the Flask app instance to be used with uvicorn
def create_app_for_uvicorn():
    from starlette.middleware.wsgi import WSGIMiddleware
    flask_app = get_custom_gui_app(demo=False)
    return WSGIMiddleware(flask_app)

app = create_app_for_uvicorn()

if __name__ == "__main__":
    import argparse
    # Run the GUI with extended provider support
    parser = argparse.ArgumentParser(description='Run the GUI with extended provider support')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=7000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--demo', action='store_true', help='Enable demo mode')
    
    args = parser.parse_args()
    run_gui(host=args.host, port=args.port, debug=args.debug, demo=args.demo)