"""
Final test to verify the completely restructured API
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

def test_complete_api():
    """Test that we can import the complete restructured API"""
    try:
        print("Testing complete restructured API imports...")
        
        # Test importing from the main custom_inference_api module
        print("Importing from custom_inference_api...")
        from examples.custom_inference_api import (
            AppConfig,
            get_name_and_provider,
            get_model_by_providers,
            create_app,
            create_app_debug,
            ErrorResponse,
            Api,
            format_exception,
        )
        print("✓ custom_inference_api imported successfully")
        
        # Test that we can create an AppConfig instance
        print("Testing AppConfig...")
        AppConfig.set_config(model="test-model", provider="test-provider")
        print(f"✓ AppConfig.model: {AppConfig.model}")
        print(f"✓ AppConfig.provider: {AppConfig.provider}")
        
        # Test utility functions
        print("Testing utility functions...")
        name, provider = get_name_and_provider("gpt-4o:OpenaiChat")
        print(f"✓ get_name_and_provider: name={name}, provider={provider}")
        
        # Test that Api class is accessible
        print("Testing Api class...")
        print(f"✓ Api class: {Api}")
        
        # Test that ErrorResponse is accessible
        print("Testing ErrorResponse...")
        print(f"✓ ErrorResponse class: {ErrorResponse}")
        
        print("\n✓ All complete API tests passed! The restructuring was successful.")
        return True
        
    except Exception as e:
        print(f"✗ Complete API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_api()
    if not success:
        sys.exit(1)