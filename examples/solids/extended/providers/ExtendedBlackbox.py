from g4f.Provider import Blackbox
from g4f.typing import Messages, AsyncResult
from typing import Optional

class ExtendedBlackbox(Blackbox):
    """Extended Blackbox provider with additional functionality"""
    
    # Inherit class attributes from the parent class
    # working = True
    # supports_stream = True
    is_extended=True
    
    # Add any additional class attributes or methods here
    def __init__(self):
        super().__init__()
        # Initialize any additional attributes
        
    @classmethod
    async def create_async_generator(
        cls,
        model: str,
        messages: Messages,
        # Add any additional parameters you want to support
        custom_param: Optional[str] = None,
        **kwargs
    ) -> AsyncResult:
        """
        Overridden version of create_async_generator with additional features
        """
        # Add your custom logic here before calling the original method (if needed)
        if custom_param:
            # Do something with custom_param
            print(f"Custom parameter provided: {custom_param}")
            
        # Call the parent method with all original parameters
        # You can also modify parameters before passing them
        async for result in super().create_async_generator(model, messages, **kwargs):
            # You can process or modify the results here if needed
            # For example, you could filter, transform, or add metadata to results
            yield result
 

# Define working as a module-level attribute to ensure it's available
# when the module is accessed directly
# working = ExtendedBlackbox.working
# supports_stream = ExtendedBlackbox.supports_stream

# # Define get_dict as a module-level attribute to ensure it's available
# # when the module is accessed directly
# def get_dict():
#     return ExtendedBlackbox.get_dict()

# # Also define other attributes that might be accessed directly from the module
# url = ExtendedBlackbox.url
# label = getattr(ExtendedBlackbox, 'label', None)
# __name__ = ExtendedBlackbox.__name__
