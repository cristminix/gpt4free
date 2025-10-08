"""
Application wrapper that uses Extended 
This is the cleanest approach for using your extended provider in applications.
""" 
from examples.solids.extended.providers import ExtendedBlackbox, ExtendedGLM,ExtendedLMArenaBeta,ExtendedPollinationsAI
from g4f import ChatCompletion
from g4f.models import Model
from g4f.Provider import ProviderType
from typing import Union, Optional

class ExtendedChatCompletion:
    """
    Wrapper around ChatCompletion that uses Extended by default
    """
    
    @staticmethod
    def create(
        model: Union[Model, str],
        messages: list,
        provider: Union[ProviderType, str, None] = None,
        stream: bool = False,
        **kwargs
    ):
        """
        Create a chat completion using ExtendedBlackbox
        """
        #  use Extended  instead
        if provider == "Blackbox" :
            provider = ExtendedBlackbox
        elif provider == "PollinationsAI":
            provider = ExtendedPollinationsAI
        elif provider == "LMArenaBeta":
            provider = ExtendedLMArenaBeta
        elif provider == "GLM":
                provider = ExtendedGLM
        return ChatCompletion.create(
            model=model,
            messages=messages,
            provider=provider,
            stream=stream,
            **kwargs
        )
    
    @staticmethod
    async def create_async(
        model: Union[Model, str],
        messages: list,
        provider: Union[ProviderType, str, None] = None,
        stream: bool = False,
        **kwargs
    ):
        """
        Create an async chat completion using Extended providers
        """
        # If specific provider is requested, use the extended version instead
        if provider == "Blackbox" :
            provider = ExtendedBlackbox
        elif provider == "PollinationsAI":
            provider = ExtendedPollinationsAI
        elif provider == "LMArenaBeta":
            provider = ExtendedLMArenaBeta
            
        # Dapatkan response dari ChatCompletion.create_async
        response = ChatCompletion.create_async(
            model=model,
            messages=messages,
            provider=provider,
            stream=stream,
            **kwargs
        )
        
        # Kembalikan response langsung (sudah merupakan async iterator)
        async for chunk in response:
            yield chunk

