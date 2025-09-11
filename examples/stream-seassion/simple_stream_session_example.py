import asyncio
from g4f.requests import StreamSession

async def simple_example():
    """
    Contoh sederhana penggunaan StreamSession
    """
    print("Memulai contoh StreamSession...")
    
    # Argumen untuk StreamSession
    args = {
        "impersonate": "chrome",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
        }
    }
    
    print("Membuat sesi streaming dengan StreamSession...")
    
    # Membuat sesi streaming dengan StreamSession
    # Karena ini hanya contoh, kita tidak akan membuat permintaan sebenarnya
    # tapi hanya menunjukkan bagaimana objek dibuat
    try:
        session = StreamSession(**args)
        print("Sesi StreamSession berhasil dibuat!")
        print("StreamSession siap digunakan untuk permintaan streaming.")
        
        # Menutup sesi
        await session.close()
        print("Sesi StreamSession ditutup.")
        
    except Exception as e:
        print(f"Terjadi kesalahan saat membuat StreamSession: {e}")

if __name__ == "__main__":
    asyncio.run(simple_example())