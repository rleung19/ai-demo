# PowerShell script to start both Next.js frontend and standalone API server
# Usage: .\scripts\start-all.ps1

Write-Host "============================================================" -ForegroundColor Blue
Write-Host "Starting AI Demo Application" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue

# Load environment variables from .env file
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
    Write-Host "✓ Loaded .env file" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
}

# Ensure TNS_ADMIN is set
if (-not $env:TNS_ADMIN -and $env:ADB_WALLET_PATH) {
    $env:TNS_ADMIN = $env:ADB_WALLET_PATH
    Write-Host "✓ Set TNS_ADMIN to: $env:TNS_ADMIN" -ForegroundColor Green
}

# Set API port if not set
if (-not $env:API_PORT) {
    $env:API_PORT = "3001"
}

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Blue
Write-Host "  Next.js Frontend: http://localhost:3000"
Write-Host "  API Server:       http://localhost:$env:API_PORT"
Write-Host "  TNS_ADMIN:        $($env:TNS_ADMIN ?? 'not set')"
Write-Host ""

# Start API server
Write-Host "Starting API server on port $env:API_PORT..." -ForegroundColor Blue
$apiJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    $env:API_PORT = $using:env:API_PORT
    npm run server:dev
}

# Wait a bit for API server to start
Start-Sleep -Seconds 3

# Start Next.js
Write-Host "Starting Next.js frontend on port 3000..." -ForegroundColor Blue
$nextjsJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    npm run dev
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Both servers are running!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend:  http://localhost:3000"
Write-Host "API:       http://localhost:$env:API_PORT"
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers"
Write-Host ""

# Wait for user to stop
try {
    Wait-Job -Job $apiJob, $nextjsJob
} finally {
    Stop-Job -Job $apiJob, $nextjsJob
    Remove-Job -Job $apiJob, $nextjsJob
}
