from __future__ import annotations

import sys
from pathlib import Path as PathLib

# Add the root directory to the path so we can import g4f modules
root_dir = PathLib(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# Import the original Provider module
from g4f.Provider import *

# Import the ProviderUtils class to extend it
from g4f.Provider import ProviderUtils as BaseProviderUtils

# Import extended providers
from examples.solids.extended.providers import ExtendedGLM, ExtendedLMArenaBeta, ExtendedPollinationsAI, ExtendedBlackbox

# Override original providers with extended versions
# This ensures that when importing with 'from ProviderExtended import *',
# the extended versions are available with their original names
LMArenaBeta = ExtendedLMArenaBeta
LMArena = ExtendedLMArenaBeta
PollinationsAI = ExtendedPollinationsAI
Blackbox = ExtendedBlackbox
GLM  = ExtendedGLM,
class ProviderUtils(BaseProviderUtils):
    """
    Extended ProviderUtils class that includes custom providers.
    """
    # Extend the convert dictionary with custom providers
    # Replace original providers with extended versions while keeping the same names
    convert = BaseProviderUtils.convert.copy()
    convert.update({
        "LMArenaBeta": ExtendedLMArenaBeta,
        "LMArena": ExtendedLMArenaBeta,
        "PollinationsAI": ExtendedPollinationsAI,
        "Blackbox": ExtendedBlackbox,
        "GLM"  :ExtendedGLM
    })

# Make sure all providers are available when this module is imported
# Include the extended providers in __all__ so they are imported with 'from ProviderExtended import *'
__all__ = [name for name in dir() if not name.startswith("_")]