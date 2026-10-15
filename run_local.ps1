$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$mongoData = Join-Path $root "mongo-data"
New-Item -ItemType Directory -Force -Path $mongoData | Out-Null

if (Get-Command mongod -ErrorAction SilentlyContinue) {
    $running = Get-CimInstance Win32_Process -Filter "Name='mongod.exe'" -ErrorAction SilentlyContinue
    if (-not $running) {
        Write-Host "Iniciando MongoDB em localhost:27017..."
        Start-Process mongod -ArgumentList @('--dbpath', $mongoData) -NoNewWindow
        Start-Sleep -Seconds 5
    }
}
else {
    Write-Host "MongoDB nao encontrado. Instale o MongoDB Community Edition e rode 'mongod --dbpath $mongoData' antes de continuar."
}

$backendDir = Join-Path $root "backend"
if (-not (Test-Path (Join-Path $backendDir ".venv"))) {
    Write-Host "Criando ambiente virtual do backend..."
    py -m venv (Join-Path $backendDir ".venv")
}

& (Join-Path $backendDir ".venv\Scripts\Activate.ps1")
Set-Location $backendDir
python -m pip install -r requirements.txt
python -m manage ensure-indexes
python -m manage migrate
python -m manage seed
python -m manage resume-restores
$env:FRONTEND_URL = "http://localhost:3000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$backendDir'; . '.\.venv\Scripts\Activate.ps1'; uvicorn server:app --reload --host 0.0.0.0 --port 8000" -WorkingDirectory $backendDir

$frontendDir = Join-Path $root "frontend"
Set-Location $frontendDir
if (-not (Test-Path "node_modules")) {
    Write-Host "Instalando dependencias do frontend..."
    npm install
}
$env:REACT_APP_BACKEND_URL = "http://localhost:8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$frontendDir'; npm start" -WorkingDirectory $frontendDir

Write-Host "Backend em: http://localhost:8000"
Write-Host "Frontend em: http://localhost:3000"
Write-Host "Se o MongoDB ainda nao estiver rodando, execute manualmente: mongod --dbpath '$mongoData'"
