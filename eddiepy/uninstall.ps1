param(
    [string]$InstallDirectory = "$env:LOCALAPPDATA\EddieLang"
)

$ErrorActionPreference = "Stop"
if (Test-Path -LiteralPath $InstallDirectory) {
    Remove-Item -LiteralPath $InstallDirectory -Recurse -Force
    Write-Host "Removed EddieLang runtime: $InstallDirectory"
}

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath) {
    $remainingEntries = $userPath -split ";" | Where-Object {
        $_ -and ($_.TrimEnd("\") -ine $InstallDirectory.TrimEnd("\"))
    }
    [Environment]::SetEnvironmentVariable("Path", ($remainingEntries -join ";"), "User")
}

Write-Host "EddieLang uninstall complete." -ForegroundColor Green
Write-Host "VS Code extension was kept."
Write-Host "Restart PowerShell or VS Code to refresh PATH and extensions."
