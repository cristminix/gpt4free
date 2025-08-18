"""
Test script to verify the refactored API structure
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

def test_api_modules():
    """Test that we can import the refactored API modules"""
    try:
        print("Testing refactored API imports...")
        
        # Test importing individual modules from api subdirectory
        print("Importing api.base...")
        from examples.solids.api.base import ErrorResponse, format_exception
        print("✓ api.base imported successfully")
        
        print("Importing api.core...")
        from examples.solids.api.core import Api
        print("✓ api.core imported successfully")
        
        print("Importing api.models...")
        from examples.solids.api.models import models_list, providers_list
        print("✓ api.models imported successfully")
        
        print("Importing api.chat...")
        from examples.solids.api.chat import chat_completions, v1_responses
        print("✓ api.chat imported successfully")
        
        print("Importing api.media...")
        from examples.solids.api.media import generate_image, convert
        print("✓ api.media imported successfully")
        
        print("Importing api.routes...")
        from examples.solids.api.routes import register_routes
        print("✓ api.routes imported successfully")
        
        # Test importing from the main api package
        print("Importing from api package...")
        from examples.solids.api import Api as ApiFromPackage, ErrorResponse as ErrorResponseFromPackage
        print("✓ api package imported successfully")
        
        print("\n✓ All API module tests passed! The refactoring was successful.")
        return True
        
    except Exception as e:
        print(f"✗ API module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_modules()
    if not success:
        sys.exit(1)