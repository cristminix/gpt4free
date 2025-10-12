import asyncio
import json
import os
from examples.solids.extended.providers.FactoryAI import FactoryAI

async def example_usage():
    """
    Contoh penggunaan ExtendedGLM dengan StreamSession
    """
    # Konfigurasi dasar
    model = "glm-4.6"  # Ganti dengan model yang tersedia
    messages = [
        {"role": "system", "content": "You are Black Mamba, general purpose assistant"},
        {"role": "user", "content": "Halo, apa kabar ,kamu siapa jawab pakai bahasa jawa?"}
    ]
    
   
    try:
        # Menggunakan Factory untuk membuat generator
        factory = FactoryAI()
        async for chunk in FactoryAI.create_async_generator(
            model=model,
            messages=messages, # type: ignore
            proxy=os.getenv("G4F_PROXY") # type: ignore
        ):
            # Memproses setiap chunk dari stream
            if isinstance(chunk, str):
                # String content - print directly
                print(chunk, end="", flush=True)
            elif isinstance(chunk, dict):
                # Dictionary chunk - extract delta content from legacy format
                if chunk.get("choices") and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        print(content, end="", flush=True)
            elif hasattr(chunk, 'to_json'):
                print(f"\nJSON Response: {json.dumps(chunk.to_json(), indent=2)}") # type: ignore
            elif hasattr(chunk, 'url'):
                print(f"\nImage URLs: {chunk.url}") # type: ignore
            else:
                # Fallback for other types
                print(f"\n{chunk}")
        print("")
    except Exception as e:
        print(f"{e}")

if __name__ == "__main__":
    asyncio.run(example_usage())