"""
Test script to verify the reorganized custom inference API
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

def test_imports():
    """Test that we can import the reorganized modules"""
    try:
        print("Testing imports...")
        
        # Test importing individual modules from solids
        print("Importing solids modules...")
        from examples.solids.config import AppConfig
        from examples.solids.utils import get_name_and_provider, get_model_by_providers
        from examples.solids.app import create_app, create_app_debug
        from examples.solids.api import Api, ErrorResponse, format_exception
        from examples.solids.run import run_api
        
        print("✓ All solids modules imported successfully")
        
        # Test that AppConfig is accessible
        print(f"✓ AppConfig is accessible: {AppConfig}")
        
        # Test that functions are accessible
        print(f"✓ get_name_and_provider is accessible")
        print(f"✓ get_model_by_providers is accessible")
        
        # Test that classes are accessible
        print(f"✓ Api class is accessible")
        print(f"✓ ErrorResponse class is accessible")
        
        # Test that format_exception is accessible
        print(f"✓ format_exception is accessible")
        
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing reorganized custom inference API...")
    success = test_imports()
    if success:
        print("\n✓ All tests passed! The reorganization was successful.")
    else:
        print("\n✗ Some tests failed. Please check the implementation.")