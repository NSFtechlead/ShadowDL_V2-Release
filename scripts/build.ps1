param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if ($Clean) {
    foreach ($relative in @("build", "dist", ".runtime")) {
        $target = Join-Path $root $relative
        if (Test-Path -LiteralPath $target) {
            $resolved = (Resolve-Path -LiteralPath $target).Path
            if (-not $resolved.StartsWith($root)) {
                throw "Refusing to remove outside project: $resolved"
            }
            Remove-Item -LiteralPath $resolved -Recurse -Force
        }
    }
}

$env:PYTHONUTF8 = "1"
& (Join-Path $PSScriptRoot 'prepare-runtime.ps1')
uv run --extra build pyinstaller .\ShadowDL.spec --noconfirm --clean
