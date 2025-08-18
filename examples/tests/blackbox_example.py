"""
Example usage of the extended Blackbox provider
"""

import asyncio

from examples.solids.extended.providers import ExtendedBlackbox
from examples.tests import ExtendedChatCompletion 
# Convenience functions
def chat_with_extended_blackbox(model: str = "blackboxai", messages: list = None, **kwargs):
    """
    Simple function to chat with ExtendedBlackbox
    """
    if messages is None:
        messages = [{"role": "user", "content": "Hello!"}]
        
    return ExtendedChatCompletion.create(model, messages, **kwargs)

async def async_chat_with_extended_blackbox(model: str = "blackboxai", messages: list = None, **kwargs):
    """
    Simple async function to chat with ExtendedBlackbox
    """
    if messages is None:
        messages = [{"role": "user", "content": "Hello!"}]
        
    return await ExtendedChatCompletion.create_async(model, messages, **kwargs)
async def main():
    # Example 1: Using the extended class directly
    messages = [{"role": "user", "content": "Hello, extended Blackbox!"}]
    
    print("Using extended Blackbox provider:")
    try:
        response = []
        async for chunk in ExtendedBlackbox.create_async_generator(
            "blackboxai", 
            messages,
            custom_param="example"
        ):
            if isinstance(chunk, str):
                response.append(chunk)
                print(chunk, end="", flush=True)
        print("\n" + "="*50)
        
        
        
       
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())