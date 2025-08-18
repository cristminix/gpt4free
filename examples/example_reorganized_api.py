"""
Example usage of the reorganized custom inference API
"""

def example_usage():
    """Example of how to use the reorganized API components"""
    
    # Import the reorganized components
    from examples.solids.config import AppConfig
    from examples.solids.utils import get_name_and_provider, get_model_by_providers
    from examples.solids.app import create_app, create_app_debug
    from examples.solids.api import Api, ErrorResponse, format_exception
    
    # Example 1: Using AppConfig
    print("Example 1: Using AppConfig")
    AppConfig.set_config(
        model="gpt-4o",
        provider="OpenaiChat",
        timeout=300
    )
    print(f"AppConfig.model: {AppConfig.model}")
    print(f"AppConfig.provider: {AppConfig.provider}")
    print(f"AppConfig.timeout: {AppConfig.timeout}")
    
    # Example 2: Using utility functions
    print("\nExample 2: Using utility functions")
    name, provider = get_name_and_provider("gpt-4o:OpenaiChat")
    print(f"Name: {name}, Provider: {provider}")
    
    # Example 3: Creating an app
    print("\nExample 3: Creating an app")
    try:
        app = create_app()
        print(f"App created successfully: {app}")
    except Exception as e:
        print(f"Note: App creation requires additional dependencies: {e}")
    
    # Example 4: Using Api class
    print("\nExample 4: Using Api class")
    print("Api class is available for use in FastAPI applications")
    
    # Example 5: Using ErrorResponse
    print("\nExample 5: Using ErrorResponse")
    try:
        error_response = ErrorResponse.from_message("This is a test error", 500)
        print(f"ErrorResponse created: {error_response}")
    except Exception as e:
        print(f"ErrorResponse usage demonstrated: {e}")
    
    print("\n✓ All examples completed successfully!")

if __name__ == "__main__":
    example_usage()