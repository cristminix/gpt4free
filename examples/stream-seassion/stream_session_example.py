import asyncio
import json
import os
from g4f.requests import StreamSession

async def example_streaming_request():
    """
    Contoh penggunaan StreamSession untuk membuat koneksi streaming dan menampilkan respons
    """
    # Mendapatkan proxy dari variabel lingkungan
    proxy = os.environ.get("G4F_PROXY")
    if proxy:
        print(f"Menggunakan proxy: {proxy}")
    else:
        print("Tidak menggunakan proxy")
    
    # Argumen untuk StreamSession
    args = {
        "impersonate": "chrome",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
        },
        "proxy": proxy  # Menambahkan proxy ke argumen
    }
    
    print("Membuat sesi streaming dengan StreamSession...")
    
    # Membuat sesi streaming dengan StreamSession
    async with StreamSession(**args) as session:
        print("StreamSession berhasil dibuat")
        
        # Membuat permintaan GET ke endpoint yang valid
        print("\nMembuat permintaan GET ke https://httpbin.org/get...")
        async with session.get("https://httpbin.org/get") as response:
            # Memeriksa apakah permintaan berhasil
            response.raise_for_status()
            print(f"Status respons: {response.status}")
            
            # Mendapatkan dan mencetak respons JSON
            result = await response.json()
            print("Respons GET:")
            print(json.dumps(result, indent=2))
        
        # Contoh dengan permintaan POST
        post_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello!"}]
        }
        
        print("\nMembuat permintaan POST ke https://httpbin.org/post...")
        async with session.post("https://httpbin.org/post", json=post_data) as response:
            # Memeriksa apakah permintaan berhasil
            response.raise_for_status()
            print(f"Status respons: {response.status}")
            
            # Mendapatkan dan mencetak respons JSON
            result = await response.json()
            print("Respons POST:")
            print(json.dumps(result, indent=2))

async def example_sse_streaming():
    """
    Contoh penggunaan StreamSession untuk menangani streaming respons
    """
    # Mendapatkan proxy dari variabel lingkungan
    proxy = os.environ.get("G4F_PROXY")
    if proxy:
        print(f"Menggunakan proxy: {proxy}")
    else:
        print("Tidak menggunakan proxy")
    
    # Argumen untuk StreamSession
    args = {
        "impersonate": "chrome",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
        },
        "proxy": proxy  # Menambahkan proxy ke argumen
    }
    
    print("Membuat sesi streaming dengan StreamSession untuk SSE...")
    
    # Membuat sesi streaming dengan StreamSession
    async with StreamSession(**args) as session:
        print("StreamSession untuk SSE berhasil dibuat")
        
        # Membuat permintaan ke endpoint streaming
        print("\nMembuat permintaan ke https://httpbin.org/stream/3...")
        async with session.get("https://httpbin.org/stream/3") as response:
            # Memeriksa apakah permintaan berhasil
            response.raise_for_status()
            print(f"Status respons: {response.status}")
            print("Menerima data streaming:")
            
            # Iterasi melalui baris-baris respons
            line_count = 0
            async for line in response.iter_lines():
                if line:
                    line_count += 1
                    print(f"Baris {line_count}: {line.decode('utf-8')}")
                if line_count >= 3:  # Batasi jumlah baris yang ditampilkan
                    break
            
            print(f"\nTotal baris yang diterima: {line_count}")

if __name__ == "__main__":
    # Menjalankan contoh streaming request
    print("=== Contoh Streaming Request dengan Respons ===")
    asyncio.run(example_streaming_request())
    
    # Menjalankan contoh SSE streaming
    print("\n=== Contoh SSE Streaming dengan Respons ===")
    asyncio.run(example_sse_streaming())
    
    print("\nSemua contoh telah dijalankan dengan sukses!")