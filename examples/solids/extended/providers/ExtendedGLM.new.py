import os

from platformdirs import user_config_dir
from g4f.Provider.GLM import GLM
from g4f.typing import AsyncResult, Messages
from g4f.providers.response import Usage, Reasoning
from g4f.requests import StreamSession, raise_for_status
from g4f import debug
# from __future__ import annotations
import time
import json

import uuid
import requests
class ExtendedGLM(GLM):
    pass