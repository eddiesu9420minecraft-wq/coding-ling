param(
    [string]$InstallDirectory = "$env:LOCALAPPDATA\EddieLang"
)

$ErrorActionPreference = "Stop"

$sourceDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceMain = Join-Path $sourceDirectory "main.py"
$sourceCommand = Join-Path $sourceDirectory "eddie.cmd"
$sourceExample = Join-Path $sourceDirectory "main.eddie"

if (-not (Test-Path -LiteralPath $sourceMain)) {
    throw "main.py not found: $sourceMain"
}

if (-not (Test-Path -LiteralPath $sourceCommand)) {
    throw "eddie.cmd not found: $sourceCommand"
}

New-Item -ItemType Directory -Path $InstallDirectory -Force | Out-Null
Copy-Item -LiteralPath $sourceMain -Destination (Join-Path $InstallDirectory "main.py") -Force
Copy-Item -LiteralPath $sourceCommand -Destination (Join-Path $InstallDirectory "eddie.cmd") -Force

if (Test-Path -LiteralPath $sourceExample) {
    Copy-Item -LiteralPath $sourceExample -Destination (Join-Path $InstallDirectory "main.eddie") -Force
}

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathEntries = @()

if ($userPath) {
    $pathEntries = $userPath -split ";" | Where-Object { $_ -ne "" }
}

$alreadyInPath = $pathEntries | Where-Object {
    $_.TrimEnd("\") -ieq $InstallDirectory.TrimEnd("\")
}

if (-not $alreadyInPath) {
    $newUserPath = (($pathEntries + $InstallDirectory) -join ";")
    [Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
}

Write-Host "EddieLang installation complete." -ForegroundColor Green
Write-Host "Install location: $InstallDirectory"
Write-Host "Restart PowerShell or the VS Code terminal."
Write-Host "Usage: eddie .\main.eddie"
