Param(
  [int]$Port = 8090
)

Write-Host "Starting Trinity AI Intelligence Console on port $Port..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check if Python is available
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Error "Python not found in PATH. Please install Python 3.11 or higher."
    exit 1
}

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Using: $pythonVersion" -ForegroundColor Green

# Set port environment variable
$env:PORT = "$Port"

# Check if required directories exist
if (-not (Test-Path "middleware")) {
    Write-Warning "middleware directory not found - some features may not work"
}

if (-not (Test-Path "routers")) {
    Write-Warning "routers directory not found - some features may not work"
}

# Check if requirements are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import fastapi, uvicorn" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing required dependencies..." -ForegroundColor Yellow
        python -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install dependencies. Please run: python -m pip install -r requirements.txt"
            exit 1
        }
    }
} catch {
    Write-Host "Installing required dependencies..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
}

Write-Host "`nStarting server..." -ForegroundColor Green
Write-Host "API Docs: http://localhost:$Port/api/docs" -ForegroundColor Cyan
Write-Host "Health Check: http://localhost:$Port/health/ai" -ForegroundColor Cyan
Write-Host "Main UI: http://localhost:$Port" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

# Start uvicorn
try {
    python -m uvicorn app:app --host 0.0.0.0 --port $Port --reload
}
catch {
    Write-Error "Failed to start uvicorn: $_"
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check if port $Port is already in use" -ForegroundColor Yellow
    Write-Host "2. Verify all dependencies are installed: python -m pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host "3. Check for errors in app.py" -ForegroundColor Yellow
    exit 1
}
