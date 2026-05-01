# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files


ROOT = Path.cwd()
SRC = ROOT / "src"
RUNTIME = ROOT / ".runtime"
ICON = ROOT / "assets" / "shadowdl.ico"

YT_DLP = RUNTIME / "yt-dlp.exe"
FFMPEG_DIR = RUNTIME / "ffmpeg"

if not YT_DLP.is_file():
    raise SystemExit("Missing runtime dependency: .runtime/yt-dlp.exe")

if not FFMPEG_DIR.is_dir():
    raise SystemExit("Missing runtime dependency: .runtime/ffmpeg")


datas = collect_data_files("sv_ttk")
datas.append((str(YT_DLP), "."))
datas.append((str(FFMPEG_DIR), "ffmpeg"))

a = Analysis(
    [str(SRC / "shadowdl" / "__main__.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=datas,
    hiddenimports=["sv_ttk"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ShadowDL_V2.3",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(ICON) if ICON.is_file() else None,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ShadowDL",
)
