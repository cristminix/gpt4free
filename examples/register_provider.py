"""
Custom provider registration module
This registers your extended Blackbox provider in the g4f system
"""

from examples.blackbox_extended import ExtendedBlackbox
import g4f.Provider
import g4f.providers

def register_extended_blackbox():
    """
    Register the ExtendedBlackbox provider to replace the original Blackbox
    """
    # Replace in the main Provider module
    g4f.Provider.Blackbox = ExtendedBlackbox
    
    # Update the provider map
    g4f.Provider.__map__['Blackbox'] = ExtendedBlackbox
    
    # Update in the providers list if not already there
    if ExtendedBlackbox not in g4f.Provider.__providers__:
        # Remove original Blackbox if it exists
        original_blackbox = None
        for provider in g4f.Provider.__providers__:
            if provider.__name__ == 'Blackbox':
                original_blackbox = provider
                break
        
        if original_blackbox:
            g4f.Provider.__providers__.remove(original_blackbox)
        
        # Add the extended version
        g4f.Provider.__providers__.append(ExtendedBlackbox)
        
        # Update __all__
        if 'Blackbox' in g4f.Provider.__all__:
            # Replace Blackbox with ExtendedBlackbox in __all__ if needed
            pass  # Keep the name as 'Blackbox' for compatibility
    
    print("ExtendedBlackbox registered successfully")

def register_as_new_provider():
    """
    Register the ExtendedBlackbox as a new provider (doesn't replace original)
    """
    # Add as a new provider with a different name
    g4f.Provider.ExtendedBlackbox = ExtendedBlackbox
    
    # Update the provider map
    g4f.Provider.__map__['ExtendedBlackbox'] = ExtendedBlackbox
    
    # Update in the providers list
    if ExtendedBlackbox not in g4f.Provider.__providers__:
        g4f.Provider.__providers__.append(ExtendedBlackbox)
        
    # Update __all__
    if 'ExtendedBlackbox' not in g4f.Provider.__all__:
        g4f.Provider.__all__.append('ExtendedBlackbox')
    
    print("ExtendedBlackbox registered as a new provider")

# Auto-register when this module is imported
register_extended_blackbox()