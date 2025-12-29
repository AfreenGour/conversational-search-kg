Param()

Write-Host "Starting docker smoke test..."

# Change to repository root (parent of this scripts folder)
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location -Path $repoRoot

Write-Host "Bringing up compose stack with 'docker compose'..."
docker compose up --build -d
Write-Host "Waiting for services to start..."
Start-Sleep -Seconds 10

# Run the Python smoke script from repo/tests
python .\tests\docker_smoke.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Smoke test failed with exit code $LASTEXITCODE"
    docker compose down -v
    exit $LASTEXITCODE
}

Write-Host "Smoke test completed successfully"
docker compose down -v
