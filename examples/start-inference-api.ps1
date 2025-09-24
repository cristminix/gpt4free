# PowerShell Script untuk menjalankan Inference API
# Setara dengan start-inference-api.sh

# Set environment variables
$env:PYTHONPATH = "$(Get-Location);$(Get-Location)/.deps/gpt4free"

$env:HUGGINGFACE_API_KEY=""
$env:TOGETHER_API_KEY=""

# Run the inference API
uv run python -m examples.custom_inference_api.run --debug