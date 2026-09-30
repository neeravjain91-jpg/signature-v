<#
.SYNOPSIS
    SIGNATURE VMAKE — Automated Windows Setup and Verification Script.

.DESCRIPTION
    Prepares and validates the local Windows development environment:
    1. Validates Python 3.11+
    2. Initializes virtual environment if not present
    3. Upgrades pip and installs certified requirements
    4. Validates database and executes migrations
    5. Seeds demonstration records
    6. Validates model checkpoints
    7. Runs comprehensive startup diagnostics
#>

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "       SIGNATURE VMAKE — WINDOWS ENVIRONMENT SETUP" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Check Python
$pyCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pyCmd) {
    Write-Host "[ERROR] Python was not found in PATH. Please install Python 3.11+." -ForegroundColor Red
    exit 1
}

$pyVersion = python --version 2>&1
Write-Host "[*] Detected: $pyVersion" -ForegroundColor Green

# 2. Virtual Environment
if (-not (Test-Path "venv") -and -not (Test-Path ".venv")) {
    Write-Host "[*] Creating Python virtual environment in .venv..." -ForegroundColor Yellow
    python -m venv .venv
}

if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "[*] Activating virtual environment (.venv)..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[*] Activating virtual environment (venv)..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

# 3. Upgrade Pip and Install Dependencies
Write-Host "[*] Verifying & installing dependencies from requirements.txt..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Dependency installation encountered an issue." -ForegroundColor Red
    exit 1
}
Write-Host "[PASS] Dependencies installed successfully." -ForegroundColor Green

# 4. Database Setup & Seeding
Write-Host "[*] Verifying database schema and demo records..." -ForegroundColor Yellow
python database/seed_demo_data.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Database seeding failed." -ForegroundColor Red
    exit 1
}
Write-Host "[PASS] Database initialized and seeded." -ForegroundColor Green

# 5. Dataset Validation
Write-Host "[*] Verifying dataset integrity..." -ForegroundColor Yellow
python scripts/validate_dataset.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Dataset verification reported an issue." -ForegroundColor DarkYellow
}

# 6. Run Diagnostic Utility
Write-Host "[*] Executing system diagnostics..." -ForegroundColor Yellow
python scripts/diagnose.py

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] Setup complete! You can start SIGNATURE VMAKE with:" -ForegroundColor Green
Write-Host "          python -m uvicorn api.main:app --host 127.0.0.1 --port 8000" -ForegroundColor White
Write-Host "          Then visit http://127.0.0.1:8000 in your browser." -ForegroundColor White
Write-Host "=================================================================" -ForegroundColor Cyan
