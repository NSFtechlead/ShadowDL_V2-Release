param(
    [string]$RuntimeDir = '.runtime'
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$runtimePath = Join-Path $root $RuntimeDir
$downloadPath = Join-Path $runtimePath 'downloads'

$ytDlpVersion = '2026.03.17'
$ytDlpUrl = "https://github.com/yt-dlp/yt-dlp/releases/download/$ytDlpVersion/yt-dlp.exe"
$ytDlpChecksumsUrl = "https://github.com/yt-dlp/yt-dlp/releases/download/$ytDlpVersion/SHA2-256SUMS"

$ffmpegVersion = '8.1'
$ffmpegZipUrl = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
$ffmpegVersionUrl = 'https://www.gyan.dev/ffmpeg/builds/release-version'
$ffmpegShaUrl = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip.sha256'

if (Test-Path -LiteralPath $runtimePath) {
    Remove-Item -LiteralPath $runtimePath -Recurse -Force
}

New-Item -ItemType Directory -Path $downloadPath -Force | Out-Null

$ytDlpExePath = Join-Path $runtimePath 'yt-dlp.exe'
$ytDlpChecksumsPath = Join-Path $downloadPath 'SHA2-256SUMS'

Invoke-WebRequest -Uri $ytDlpUrl -OutFile $ytDlpExePath
Invoke-WebRequest -Uri $ytDlpChecksumsUrl -OutFile $ytDlpChecksumsPath

$ytDlpExpectedHash = (
    Get-Content -LiteralPath $ytDlpChecksumsPath |
    Where-Object { $_ -match 'yt-dlp\.exe$' } |
    ForEach-Object { ($_ -split '\s+')[0].ToLowerInvariant() } |
    Select-Object -First 1
)
if (-not $ytDlpExpectedHash) {
    throw 'Impossible de trouver le hash officiel de yt-dlp.exe.'
}
$ytDlpActualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $ytDlpExePath).Hash.ToLowerInvariant()
if ($ytDlpActualHash -ne $ytDlpExpectedHash) {
    throw "Hash yt-dlp invalide: attendu $ytDlpExpectedHash, obtenu $ytDlpActualHash"
}

$ffmpegZipPath = Join-Path $downloadPath 'ffmpeg-release-essentials.zip'
$ffmpegShaPath = Join-Path $downloadPath 'ffmpeg-release-essentials.zip.sha256'
$ffmpegVerPath = Join-Path $downloadPath 'ffmpeg-release-essentials.zip.ver'
$ffmpegExtractPath = Join-Path $downloadPath 'ffmpeg_extract'

Invoke-WebRequest -Uri $ffmpegZipUrl -OutFile $ffmpegZipPath
Invoke-WebRequest -Uri $ffmpegShaUrl -OutFile $ffmpegShaPath
Invoke-WebRequest -Uri $ffmpegVersionUrl -OutFile $ffmpegVerPath

$ffmpegReportedVersion = (Get-Content -LiteralPath $ffmpegVerPath -Raw).Trim()
if ($ffmpegReportedVersion -ne $ffmpegVersion) {
    throw "Version FFmpeg inattendue: attendu $ffmpegVersion, obtenu $ffmpegReportedVersion"
}

$ffmpegExpectedHash = (Get-Content -LiteralPath $ffmpegShaPath -Raw).Trim().ToLowerInvariant()
$ffmpegActualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $ffmpegZipPath).Hash.ToLowerInvariant()
if ($ffmpegActualHash -ne $ffmpegExpectedHash) {
    throw "Hash FFmpeg invalide: attendu $ffmpegExpectedHash, obtenu $ffmpegActualHash"
}

Expand-Archive -LiteralPath $ffmpegZipPath -DestinationPath $ffmpegExtractPath -Force

$ffmpegExe = Get-ChildItem -LiteralPath $ffmpegExtractPath -Recurse -File -Filter 'ffmpeg.exe' | Select-Object -First 1
$ffprobeExe = Get-ChildItem -LiteralPath $ffmpegExtractPath -Recurse -File -Filter 'ffprobe.exe' | Select-Object -First 1
if (-not $ffmpegExe -or -not $ffprobeExe) {
    throw 'Impossible de trouver ffmpeg.exe ou ffprobe.exe après extraction.'
}

$runtimeBinDir = Join-Path $runtimePath 'ffmpeg\bin'
New-Item -ItemType Directory -Path $runtimeBinDir -Force | Out-Null
Copy-Item -LiteralPath $ffmpegExe.FullName -Destination (Join-Path $runtimeBinDir 'ffmpeg.exe') -Force
Copy-Item -LiteralPath $ffprobeExe.FullName -Destination (Join-Path $runtimeBinDir 'ffprobe.exe') -Force

Write-Host "Runtime prêt dans $runtimePath"
