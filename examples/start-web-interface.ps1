# PowerShell Script untuk menjalankan Web Interface
# Setara dengan start-web-interface.sh

# Set environment variables
$env:PYTHONPATH = "$(Get-Location);$(Get-Location)/.deps/gpt4free"

# $env:G4F_PROXY = "http://127.0.0.1:8081"
$env:G4F_PROXY = ""
# Run the web interface
uv run python -m examples.custom_inference_api.web_interface --debug