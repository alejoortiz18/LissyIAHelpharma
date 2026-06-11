# Inicia GestionPersonal.Web en http://localhost:5002
$ErrorActionPreference = "Stop"
$web = Join-Path $PSScriptRoot "GestionPersonal.Web"
$env:ASPNETCORE_ENVIRONMENT = "Development"

Write-Host "Iniciando aplicacion en http://localhost:5002 ..." -ForegroundColor Cyan
Write-Host "Presione Ctrl+C para detener." -ForegroundColor DarkGray

Set-Location $web
dotnet run --launch-profile http
