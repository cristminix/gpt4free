# GPT4Free Development Environment

GPT4Free adalah proyek open-source yang menyediakan akses gratis ke berbagai model AI melalui berbagai penyedia layanan. Proyek ini memungkinkan pengguna untuk menggunakan model AI canggih tanpa biaya berlangganan atau API keys.

## Prasyarat Sistem

Sebelum memulai, pastikan sistem Anda memiliki:

- Git
- Node.js (versi 22 atau lebih baru)
- pnpm (dapat diinstal dengan `npm install -g pnpm`)
- Python (versi 3.11 atau lebih baru)
- uv (dapat diinstal dengan `pip install uv`)

## Instalasi

### Mengunduh Dependensi

```bash
mkdir -p .deps
cd .deps
git clone https://github.com/xtekky/gpt4free
git clone https://github.com/cristminix/gpt4dev
```

### Membangun gpt4dev

```bash
cd .deps/gpt4dev
mv src/global/store/config.ts src/global/store/config-old.ts
mv src/global/store/config-g4f.ts src/global/store/config.ts
pnpm i
npx vite build
./cp-build-assets.sh
```

### Menginstal Dependensi Python

```bash
uv sync
```

### Inisialisasi Database SQLite

```bash
uv run python examples/custom_inference_api/init_database.py
```

## Menjalankan Aplikasi

### Antarmuka Web gpt4dev

Untuk memulai antarmuka web gpt4dev pada port 7000:

```bash
./examples/start-web-interface.sh
```

### API Inference Kustom

Untuk memulai API inference kustom pada port 1337:

```bash
./examples/start-inference-api.sh
```

### API Inference Kustom (Mode Pengembangan)

Untuk memulai API inference kustom dalam mode pengembangan pada port 1337:

```bash
./examples/start-inference-api-dev.sh
```

## Struktur Proyek

- `.deps/` - Direktori untuk dependensi eksternal
- `examples/` - Contoh-contoh penggunaan dan skrip
- `examples/custom_inference_api/` - Implementasi API inference kustom
- `examples/solids/` - Contoh-contoh berbasis SolidJS
- `examples/stream-seassion/` - Contoh-contoh streaming sesi

## Kontribusi

Kontribusi sangat diterima! Silakan fork proyek ini, buat perubahan Anda, dan kirimkan pull request. Pastikan untuk mengikuti pedoman pengembangan yang ada dalam proyek.

## Lisensi

Proyek ini dilisensikan di bawah lisensi MIT - lihat file [LICENSE](LICENSE) untuk detail selengkapnya.

## Dukungan dan Komunitas

Jika Anda menemukan masalah atau memiliki pertanyaan, silakan buka issue di repositori. Kami juga mendorong kontribusi dari komunitas untuk membuat proyek ini lebih baik bagi semua orang.
