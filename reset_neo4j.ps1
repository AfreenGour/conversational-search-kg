<#
Reset Neo4j data volume for this project. WARNING: destructive.
This runs `docker compose down -v` to remove volumes and then restarts the stack.
Double-click or run from PowerShell.
#>

Set-StrictMode -Version Latest
cls
Write-Host "This will remove the Neo4j data volume for this project. This is destructive." -ForegroundColor Yellow
$confirm = Read-Host -Prompt "Type YES to confirm and continue"
if ($confirm -ne 'YES') { Write-Host "Aborting." -ForegroundColor Cyan; exit 0 }

Write-Host "Stopping and removing compose (including volumes)..." -ForegroundColor Cyan
try {
    docker compose down -v
    Write-Host "Compose down -v completed." -ForegroundColor Green
} catch {
    Write-Host "Failed to run docker compose down -v: $_" -ForegroundColor Red
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

Write-Host "You can now start fresh by running run_docker.ps1" -ForegroundColor Cyan
Read-Host -Prompt "Press Enter to exit"
