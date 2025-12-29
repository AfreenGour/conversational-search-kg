<#
One-click stop helper: stops and removes containers and network created by docker compose.
Keeps volumes by default. Double-click or run from PowerShell.
#>

Set-StrictMode -Version Latest
cls
Write-Host "Stopping compose services..." -ForegroundColor Cyan
try {
    docker compose down
    Write-Host "Compose stopped." -ForegroundColor Green
} catch {
    Write-Host "Failed to stop compose stack: $_" -ForegroundColor Red
}

Read-Host -Prompt "Press Enter to exit"
