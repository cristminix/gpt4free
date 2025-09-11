import asyncio
import json
from examples.solids.extended.providers.ExtendedLMArenaBeta import ExtendedLMArenaBeta
from g4f.requests import StreamSession

async def example_usage():
    """
    Contoh penggunaan ExtendedLMArenaBeta dengan StreamSession
    """
    # Konfigurasi dasar
    model = "gpt-4"  # Ganti dengan model yang tersedia
    messages = [
        {"role": "user", "content": "Halo, apa kabar?"}
    ]
    
    # Mendapatkan argumen dari nodriver (ini akan menangani autentikasi dan mendapatkan cookies)
    # Perhatikan bahwa ini memerlukan instalasi nodriver
    # args = await ExtendedLMArenaBeta.get_args_from_nodriver(ExtendedLMArenaBeta.url)
    
    # Untuk contoh ini, kita akan menggunakan argumen placeholder
    # Dalam praktiknya, Anda akan menggunakan hasil dari get_args_from_nodriver
    args = {
        "impersonate": "chrome",
        "cookies": {},  # Cookies akan diisi setelah autentikasi
        "headers": {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "proxy": None
    }
    
    # Membuat sesi streaming dengan StreamSession
    async with StreamSession(**args) as session:
        # Menggunakan ExtendedLMArenaBeta untuk membuat generator
        async for chunk in ExtendedLMArenaBeta.create_async_generator(
            model=model,
            messages=messages,
            proxy=args.get("proxy")
        ):
            # Memproses setiap chunk dari stream
            if isinstance(chunk, str):
                print(chunk, end="", flush=True)
            elif hasattr(chunk, 'to_json'):
                print(f"\nJSON Response: {json.dumps(chunk.to_json(), indent=2)}")
            elif hasattr(chunk, 'url'):
                print(f"\nImage URLs: {chunk.url}")
            else:
                print(f"\n{chunk}")

if __name__ == "__main__":
    asyncio.run(example_usage())