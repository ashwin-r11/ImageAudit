# Run backend with project .venv (avoids system uvicorn missing cv2)
$ErrorActionPreference = "Stop"
$BackendDir = $PSScriptRoot
$RepoRoot = Resolve-Path (Join-Path $BackendDir "..")
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Error "Missing .venv at $RepoRoot\.venv — create it and pip install -r backend\requirements.txt"
}
Set-Location $BackendDir
$env:PYTHONPATH = "."
Write-Host "Using $VenvPython"
& $VenvPython -m uvicorn app.main:app --host 0.0.0.0 --port 8000 @args
