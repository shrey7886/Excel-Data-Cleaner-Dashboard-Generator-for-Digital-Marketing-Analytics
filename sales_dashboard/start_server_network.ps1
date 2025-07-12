# PowerShell script to start Django server accessible on local network
Write-Host "🌐 Starting Django server on local network..." -ForegroundColor Green

# Get local IP address
$localIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi" | Where-Object {$_.IPAddress -notlike "169.254.*"}).IPAddress
if (-not $localIP) {
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet" | Where-Object {$_.IPAddress -notlike "169.254.*"}).IPAddress
}

if ($localIP) {
    Write-Host "📍 Your local IP: $localIP" -ForegroundColor Yellow
    Write-Host "🌐 Access URL: http://$localIP`:8000" -ForegroundColor Cyan
    Write-Host "📱 Others on same WiFi can access: http://$localIP`:8000" -ForegroundColor Green
} else {
    Write-Host "⚠️  Could not detect local IP. Using 0.0.0.0" -ForegroundColor Yellow
    $localIP = "0.0.0.0"
}

Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host "==================================================" -ForegroundColor Gray

# Start Django server
python manage.py runserver $localIP`:8000 