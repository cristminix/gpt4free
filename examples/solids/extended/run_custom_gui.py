"""
Custom web interface to run the GUI with extended providers.
"""
import sys
from pathlib import Path

# Add the root directory to the Python path so we can import g4f modules
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

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
    from g4f.gui.server.app import create_app
    from g4f.gui.server.website import Website
    
    # Import our custom backend API
    from examples.solids.extended.custom_backend_api import CustomBackend_Api
    
    def get_custom_gui_app(demo: bool = False, timeout: int = None):
        """
        Create a Flask app with custom backend API support.
        """
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

    config = {
        'host': host,
        'port': port,
        'debug': debug
    }

    app = get_custom_gui_app(demo=demo)
    
    print(f"Running on port {config['port']} (http://{host}:{port}/)")
    print("You can now select 'ExtendedLMArenaBeta' as a provider in the GUI")
    app.run(**config)
    print(f"Closing port {config['port']}")

if __name__ == "__main__":
    # Run the GUI with extended provider support
    run_gui(port=7000)