from etc.unittest import asyncio
import examples.custom_inference_api
from examples.custom_inference_api.model_info import MODEL_INFO
from g4f import Provider
import g4f
from examples.custom_inference_api import AppConfig
from g4f.providers.any_provider import AnyProvider,PROVIERS_LIST_1
def models():
    model_by_providers = []
    models =  MODEL_INFO
    for model in models:
        # print(model)
        # pass
        for provider_name in model["providers"]:
            model_by_providers.append({
                    "id": f"{model["name"]}:{provider_name}",
                    "object": "model",
                    "created": 0,
                    "owned_by": "",
                    "image": model["image"],
                    "vision": model["vision"],
                    "provider": provider_name,
                } 
            )
    print(model_by_providers)
    pass
    # return {
    #     "object": "list",
    #     "data": [{
    #         "id": model,
    #         "object": "model",
    #         "created": 0,
    #         "owned_by": "",
    #         "image": isinstance(model, g4f.models.ImageModel),
    #         "vision": isinstance(model, g4f.models.VisionModel),
    #         "provider": False,
    #     } for model in AnyProvider.get_models()] +
    #     [{
    #         "id": provider_name,
    #         "object": "model",
    #         "created": 0,
    #         "owned_by": getattr(provider, "label", ""),
    #         "image": bool(getattr(provider, "image_models", False)),
    #         "vision": bool(getattr(provider, "vision_models", False)),
    #         "provider": True,
    #     } for provider_name, provider in Provider.ProviderUtils.convert.items()
    #         if provider.working and provider_name not in ("Custom")
    #     ]
    # }
if __name__ == "__main__":
    
    models()
    pass