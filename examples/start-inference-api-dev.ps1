# PowerShell Script untuk menjalankan Inference API Development
# Setara dengan start-inference-api-dev.sh

# Set environment variables
$env:PYTHONPATH = "$(Get-Location):$(Get-Location)/.deps/gpt4free"
# $env:HUGGINGFACE_API_KEY="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"
# $env:TOGETHER_API_KEY="3777726a26bc5ae7982cc15ded1db1315bbf34005b78569636a8e819cf34e365"
# $env:OPENAI_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0IjoiYXUiLCJ2IjoiMC4wLjAiLCJ1dSI6ImRpbzd0bCtQUnB5aHRneUM1djMvNUE9PSIsImF1Ijoia0hWQnFuVVNWb3V2WjU5ck9EcFR5Zz09IiwicyI6IjNJUFpyWjBtbjNFT0Y0emVYYS96S1E9PSIsImlhdCI6MTc1MjU2NzUzOX0.JfdMviNcwbx0YKyANrhsaykOAUV7lYwyMgHXlu-hjcE"
$env:G4F_PROXY = "http://127.0.0.1:8081"

# uv run python3 -m examples.custom_inference_api.run --debug
uv run uvicorn examples.custom_inference_api:create_app_debug --host 0.0.0.0 --port 1337 --reload