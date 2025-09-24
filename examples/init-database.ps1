# PowerShell Script untuk menginisialisasi database
# Script untuk membuat tabel database yang diperlukan

# Set environment variables
$env:PYTHONPATH = "$(Get-Location);$(Get-Location)/.deps/gpt4free"

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Green

try {
    uv run python examples/custom_inference_api/init_database.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database initialization completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Database initialization failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "Error occurred during database initialization: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
