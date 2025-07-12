Write-Host "🚀 Starting Digital Marketing Analytics Dashboard..." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Change to the script directory
Set-Location $PSScriptRoot

Write-Host "🦙 Starting Ollama with Llama 3..." -ForegroundColor Yellow
python start_server.py

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 