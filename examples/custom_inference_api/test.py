# from etc.unittest import asyncio
import json
import os
import requests
import examples.custom_inference_api
from examples.custom_inference_api.model_info import MODEL_INFO
from g4f import Provider
import g4f
from examples.custom_inference_api import AppConfig
from g4f.providers.any_provider import AnyProvider,PROVIERS_LIST_1
blacklisted=["AnyProvider","OpenRouter","OpenRouterFree","FenayAI","Ollama","BlackboxPro","Anthropic","Azure"]
def models():
    print("Model Aliases by Provider:")
    print("=" * 50)

    
    # Buat direktori untuk menyimpan file JSON jika belum ada
    output_dir = "examples/provider_models"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for provider_name, provider in Provider.ProviderUtils.convert.items():
        if provider_name in blacklisted:
            continue
        if hasattr(provider,"get_models"):
            try:
                if provider.working:
                    print(provider_name)
                    response = requests.get(f"http://localhost:5173/api/backend-api/v2/models/{provider_name}")
                    response.raise_for_status()  # Raise an exception for bad status codes
                    models = response.json()
                    
                    # Simpan model ke file JSON dengan nama berdasarkan provider_name
                    if models:
                        filename = os.path.join(output_dir, f"{provider_name}.json")
                        with open(filename, 'w') as f:
                            json.dump(models, f, indent=2)
                        print(f"Models for {provider_name} saved to {filename}")
                    
                    # for model in models:
                    #     print(f"{provider_name}:{model}")
            except Exception as e:
                print(f"Error processing {provider_name}: {str(e)}")
                print("blaclisted-->",provider_name)
                pass
def get_model_by_providers():
    output_dir = "@examples/provider_models"
    
    
    model_by_providers = []
    models =  MODEL_INFO
    for provider_name, provider in Provider.ProviderUtils.convert.items():
        if provider_name in blacklisted:
            continue
        filename = os.path.join(output_dir, f"{provider_name}.json")
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                models = json.load(f)
        else:
            models = []
        for model in models:
            try:
                model_name = model.get("model", model.get("label", "unknown_model"))
                model_by_providers.append({
                    "id": f"{model_name}:{provider_name}",
                    "object": "model",
                    "created": 0,
                    "owned_by": "",
                    "image": model.get("image", False),
                    "vision": model.get("vision", False),
                    "provider": provider_name,
                })
            except Exception as e:
                print(f"Error processing model for {provider_name}: {str(e)}")
                pass
    return model_by_providers
if __name__ == "__main__":
    
    models_by_providers=get_model_by_providers()
    print(models_by_providers)
    pass