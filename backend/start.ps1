# Script PowerShell para iniciar o servidor FastAPI corretamente
Write-Host "Iniciando servidor Lumine API..." -ForegroundColor Green
Write-Host ""

# Garantir que estamos no diretório correto
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "Diretório atual: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Executar o servidor
python run.py

