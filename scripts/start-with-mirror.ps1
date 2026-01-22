<#
Try pulling Redis from a list of candidate mirrors and start docker compose.
Run from repo root (PowerShell, may require admin for some operations):
  .\scripts\start-with-mirror.ps1
#>

$mirrors = @(
    "registry.cn-hangzhou.aliyuncs.com/library/redis:7",
    "hub-mirror.c.163.com/library/redis:7",
    "registry.cn-hangzhou.aliyuncs.com/library/redis:7-alpine",
    "docker.io/library/redis:7",
    "redis:7"
)

$success = $false
foreach ($img in $mirrors) {
    Write-Host "Trying image: $img"
    $Env:REDIS_IMAGE = $img
    try {
        docker pull $img
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Pulled $img successfully. Using this image for compose."
            $success = $true
            break
        }
    } catch {
        Write-Warning "pull failed for $img"
    }
}

if (-not $success) {
    Write-Warning "Unable to pull any candidate Redis image. You may need to configure Docker proxy or use a reachable mirror."
    exit 1
}

# Run compose with the selected REDIS_IMAGE
Write-Host "Starting docker compose with REDIS_IMAGE=$Env:REDIS_IMAGE"
docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    Write-Error "docker compose failed"
    exit 1
}

Write-Host "Compose started. Check services with: docker compose ps"
Write-Host "Check backend at http://localhost:8000/openapi.json"

*** End Patch