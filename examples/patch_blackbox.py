"""
Runtime patch to replace original Blackbox with ExtendedBlackbox
This allows the entire application to use your extended version without modifying original files.
"""

# Import your extended provider
from examples.blackbox_extended import ExtendedBlackbox

# Import the original provider module
import g4f.Provider

# Replace the original Blackbox with your extended version
g4f.Provider.Blackbox = ExtendedBlackbox

# Also update the provider map to ensure it's properly registered
import g4f.Provider
g4f.Provider.__map__['Blackbox'] = ExtendedBlackbox

# If you want to ensure it's also in the providers list
if ExtendedBlackbox not in g4f.Provider.__providers__:
    g4f.Provider.__providers__.append(ExtendedBlackbox)

print("Blackbox provider successfully replaced with ExtendedBlackbox")