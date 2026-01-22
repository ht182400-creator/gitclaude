<#
Install Docker Desktop on Windows via winget or Chocolatey.

Usage (run as Administrator PowerShell):
  .\scripts\install-docker-windows.ps1

This script will:
 - Check for existing `docker` command
 - Try to install via `winget` (recommended)
 - Fallback to Chocolatey if winget is not available
 - Optionally run `wsl --install` if WSL is not present

Notes:
 - Docker Desktop requires virtualization/WSL2 on modern Windows. Follow prompts.
 - After installation, start Docker Desktop once and ensure it is running before using `docker`.
#>

function Assert-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Error "This script must be run as Administrator. Right-click PowerShell -> Run as administrator."
        exit 1
    }
}

Assert-Admin

Write-Host "Checking for existing Docker..."
try {
    $ver = & docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Docker already installed:" $ver
        exit 0
    }
} catch {}

if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "Installing Docker Desktop via winget..."
    winget install --id Docker.DockerDesktop -e --source winget
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "winget install failed. You may need to run the command interactively or install via the website."
    }
} elseif (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "Installing Docker Desktop via Chocolatey..."
    choco install docker-desktop -y
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "choco install failed. You may need to run the command interactively."
    }
} else {
    Write-Host "Neither winget nor Chocolatey found. Opening Docker Desktop downloads page..."
    Start-Process "https://www.docker.com/products/docker-desktop"
    Write-Host "Please download and install Docker Desktop manually, then re-run this script."
    exit 1
}

Write-Host "Installation command finished. If Docker Desktop installer ran, please start Docker Desktop now and follow any prompts (WSL2 enablement, reboot)."
Write-Host "You can optionally install WSL2 now (recommended for Docker Desktop):"
if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
    Write-Host "WSL is not available. To install WSL2 run: wsl --install (may require reboot)."
}

Write-Host "After Docker Desktop is running, verify with:"
Write-Host "  docker --version"
Write-Host "  docker compose version"

Write-Host "When Docker is ready, return here and run from repo root:"
Write-Host "  docker compose up --build"
