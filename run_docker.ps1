<#
Run this script from Explorer (double-click) or PowerShell to build and start the compose stack.
It will try `docker compose up --build -d`, show logs, and detect common registry/proxy errors
and print clear next steps if the image pull fails (for example the registry.docker-cn.com error).

Usage:
  Right-click -> Run with PowerShell OR from a PowerShell prompt:
    .\run_docker.ps1
#>

[CmdletBinding()]
param(
    [switch]$NoPause
)

Set-StrictMode -Version Latest
cls
Write-Host "== Conversational_Search_KG: Docker helper ==" -ForegroundColor Cyan

function SuggestFixes() {
    Write-Host "";
    Write-Host "Common fixes for registry/connection errors:" -ForegroundColor Yellow
    Write-Host " 1) Open Docker Desktop -> Settings -> Docker Engine and remove/replace any 'registry-mirrors' pointing to registry.docker-cn.com." -ForegroundColor White
    Write-Host " 2) If you're behind a corporate proxy, configure it under Docker Desktop -> Settings -> Resources -> Proxies." -ForegroundColor White
    Write-Host " 3) Restart Docker Desktop after changes and re-run this script." -ForegroundColor White
    Write-Host " 4) Test pulling the base image manually: 'docker pull python:3.10-slim'" -ForegroundColor White
}

try {
    docker version > $null 2>&1
} catch {
    Write-Host "Docker CLI not available or Docker Desktop not running." -ForegroundColor Red
    Write-Host "Please start Docker Desktop and retry." -ForegroundColor White
    if (-not $NoPause) { Read-Host -Prompt "Press Enter to exit" }
    exit 1
}

Write-Host "Running: docker compose up --build -d" -ForegroundColor Green
try {
    $out = docker compose up --build -d 2>&1
    $rc = $LASTEXITCODE
} catch {
    $out = $_.Exception.Message
    $rc = 1
}

Write-Host ""; Write-Host $out

if ($rc -ne 0) {
    Write-Host ""; Write-Host "Compose failed (exit code $rc)." -ForegroundColor Red

    $txt = $out -join "`n"
    if ($txt -match "registry\.docker-cn\.com" -or $txt -match "failed to resolve source metadata" -or $txt -match "failed to do request" -or $txt -match "no such host") {
        Write-Host "Detected registry/connection error." -ForegroundColor Yellow
        SuggestFixes
    }

    Write-Host ""; Write-Host "Recent service logs (kg_service):" -ForegroundColor Cyan
    docker compose logs --tail=200 kg_service 2>&1 | Write-Host
    Write-Host ""; Write-Host "Recent service logs (neo4j):" -ForegroundColor Cyan
    docker compose logs --tail=200 neo4j 2>&1 | Write-Host

    if (-not $NoPause) { Read-Host -Prompt "Press Enter to exit" }
    exit $rc
}

Write-Host ""; Write-Host "Compose started successfully." -ForegroundColor Green
docker compose ps

# Wait for services to report Up (up to 120s)
Write-Host "Waiting for services to be Up (max 120s)..." -ForegroundColor Cyan
$start = Get-Date
$ready = $false
while ((Get-Date) - $start -lt (New-TimeSpan -Seconds 120)) {
    $ps = docker compose ps 2>&1 | Out-String
    if ($ps -match "kg_service" -and $ps -match "Up" -and $ps -match "neo4j" -and $ps -match "Up") {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 3
}

if (-not $ready) {
    Write-Host "Services did not become ready within timeout. Check logs." -ForegroundColor Yellow
    docker compose logs --tail=200 kg_service | Write-Host
    docker compose logs --tail=200 neo4j | Write-Host
    if (-not $NoPause) { Read-Host -Prompt "Press Enter to exit" }
    exit 2
}

Write-Host "Services are Up. Running smoke helper script..." -ForegroundColor Green
$logDir = Join-Path $PSScriptRoot 'run-logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

# Start background job to stream compose logs into a file so we have continuous logs
$composeLog = Join-Path $logDir 'compose.log'
Write-Host "Streaming compose logs to $composeLog" -ForegroundColor Cyan
Start-Job -Name StreamComposeLogs -ScriptBlock {
    param($ld)
    docker compose logs -f --tail=200 kg_service neo4j 2>&1 | Out-File -FilePath (Join-Path $ld 'compose.log') -Encoding utf8 -Append
} -ArgumentList $logDir | Out-Null

# Run the smoke helper and capture output
$smokeLog = Join-Path $logDir 'smoke.log'
if (Test-Path (Join-Path $PSScriptRoot 'scripts\run_smoke.ps1')) {
    Write-Host "Executing smoke helper, logging to $smokeLog" -ForegroundColor Cyan
    try {
        & .\scripts\run_smoke.ps1 *>&1 | Tee-Object -FilePath $smokeLog
        $smokeRc = $LASTEXITCODE
    } catch {
        $_ | Out-String | Tee-Object -FilePath $smokeLog
        $smokeRc = 1
    }
} else {
    Write-Host "Smoke helper not found; running basic health check against http://localhost:8000/" -ForegroundColor Yellow
    try {
        Invoke-RestMethod -Method Get -Uri http://localhost:8000/ *>&1 | Tee-Object -FilePath $smokeLog
        $smokeRc = 0
    } catch {
        $_ | Out-String | Tee-Object -FilePath $smokeLog
        $smokeRc = 1
    }
}

if ($smokeRc -eq 0) {
    Write-Host "Smoke checks passed. Logs saved in $logDir" -ForegroundColor Green
} else {
    Write-Host "Smoke checks FAILED. Gathering diagnostics to $logDir" -ForegroundColor Red
    docker compose ps 2>&1 | Out-File (Join-Path $logDir 'compose-ps.log') -Encoding utf8
    docker compose logs --tail=500 kg_service 2>&1 | Out-File (Join-Path $logDir 'kg_service.log') -Encoding utf8
    docker compose logs --tail=500 neo4j 2>&1 | Out-File (Join-Path $logDir 'neo4j.log') -Encoding utf8
    Get-ChildItem -Path $PSScriptRoot -Recurse -Depth 1 | Out-File (Join-Path $logDir 'tree.txt')
    Write-Host "Collected diagnostics. Review files in $logDir and paste relevant logs if you need help." -ForegroundColor Yellow
}

Write-Host ""; Write-Host "Done." -ForegroundColor Cyan
Write-Host "Logs folder: $logDir" -ForegroundColor White
if (-not $NoPause) { Read-Host -Prompt "Press Enter to exit" }
exit $smokeRc
