# Development

## Installing Dependencies

```bash
mkdir -p .deps
cd .deps
git clone https://github.com/xtekky/gpt4free
git clone https://github.com/cristminix/gpt4dev

```

## Building gpt4dev

```bash
cd .deps/gpt4dev
mv   src/global/store/config.ts src/global/store/config-old.ts
mv  src/global/store/config-g4f.ts src/global/store/config.ts
pnpm i
npx vite build
./cp-build-assets.sh
```

## Installing python dependencies

```bash
uv sync
```

## Init sqlite database

```bash
uv run python examples/custom_inference_api/init_database.py
```

## Running the examples

Start gpt4dev web interface on port 7000

```bash
./examples/start-web-interface.sh
```

Start custom inference api on port 1337

```bash
./examples/start-inference-api.sh
```

Start custom inference api development on port 1337

```bash
./examples/start-inference-api-dev.sh
```
