<#
Safe cleanup helper to remove common terminal/build problems.

What it does:
 - Stops and removes compose containers and network (`docker compose down`)
 - Removes exited containers and dangling images (`docker container prune`, `docker image prune`)
 - Clears `run-logs` produced by the helper scripts
 - Does NOT remove volumes unless you confirm (destructive)

Run by double-clicking this file or from PowerShell:
  .\clear_problems.ps1
#>

Set-StrictMode -Version Latest
cls
Write-Host "== Conversational_Search_KG: Safe cleanup ==" -ForegroundColor Cyan

function PauseIfInteractive() {
    param([switch]$NoPause)
    if (-not $NoPause) { Read-Host -Prompt "Press Enter to continue" }
}

Write-Host "Stopping compose stack (if running)..." -ForegroundColor Yellow
try {
    docker compose down --remove-orphans 2>&1 | Write-Host
} catch {
    Write-Host "docker compose down failed or Docker not running: $_" -ForegroundColor Red
}

Write-Host "Removing exited containers..." -ForegroundColor Yellow
try {
    docker container prune -f 2>&1 | Write-Host
} catch {
    Write-Host "docker container prune failed: $_" -ForegroundColor Red
}

Write-Host "Removing dangling images..." -ForegroundColor Yellow
try {
    docker image prune -f 2>&1 | Write-Host
} catch {
    Write-Host "docker image prune failed: $_" -ForegroundColor Red
}

$logDir = Join-Path $PSScriptRoot 'run-logs'
if (Test-Path $logDir) {
    Write-Host "Clearing run logs at $logDir" -ForegroundColor Yellow
    try {
        Remove-Item -Path (Join-Path $logDir '*') -Force -Recurse -ErrorAction Stop
        Write-Host "run-logs cleared." -ForegroundColor Green
    } catch {
        Write-Host "Failed to clear run-logs: $_" -ForegroundColor Red
    }
} else {
    Write-Host "No run-logs directory found, skipping." -ForegroundColor Cyan
}

Write-Host ""; Write-Host "If you want to also remove all unused volumes (destructive), type YES now." -ForegroundColor Yellow
$confirm = Read-Host -Prompt "Remove unused volumes? Type YES to confirm"
if ($confirm -eq 'YES') {
    Write-Host "Removing unused volumes..." -ForegroundColor Yellow
    try {
        docker volume prune -f 2>&1 | Write-Host
        Write-Host "Volumes pruned." -ForegroundColor Green
    } catch {
        Write-Host "docker volume prune failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "Skipping volume removal." -ForegroundColor Cyan
}

Write-Host "Cleanup finished." -ForegroundColor Green
PauseIfInteractive
