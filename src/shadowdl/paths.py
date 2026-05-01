import os
import shutil
import sys
from pathlib import Path


RUNTIME_CACHE_DIRNAME = '.runtime'


def is_frozen() -> bool:
    return bool(getattr(sys, 'frozen', False))


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def runtime_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return project_root()


def bundle_dir() -> Path | None:
    bundle = getattr(sys, '_MEIPASS', None)
    return Path(bundle).resolve() if bundle else None


def runtime_cache_dir() -> Path:
    return project_root() / RUNTIME_CACHE_DIRNAME


def runtime_candidates(base_dir: Path | None = None) -> list[Path]:
    if base_dir is not None:
        return [base_dir]

    candidates = [runtime_dir()]
    bundled = bundle_dir()
    if bundled is not None and bundled not in candidates:
        candidates.append(bundled)

    if not is_frozen():
        cache_dir = runtime_cache_dir()
        if cache_dir not in candidates:
            candidates.append(cache_dir)

    return candidates


def local_ffmpeg_bin_dir(base_dir: Path | None = None) -> Path | None:
    names = ('ffmpeg.exe', 'ffprobe.exe') if os.name == 'nt' else ('ffmpeg', 'ffprobe')
    for base in runtime_candidates(base_dir):
        ffmpeg_dir = base / 'ffmpeg' / 'bin'
        if all((ffmpeg_dir / name).is_file() for name in names):
            return ffmpeg_dir
    return None


def ytdlp_cmd_base(base_dir: Path | None = None) -> list[str]:
    for base in runtime_candidates(base_dir):
        for name in ('yt-dlp.exe', 'yt-dlp'):
            local = base / name
            if local.is_file():
                return [str(local)]

    path_cmd = shutil.which('yt-dlp') or shutil.which('yt-dlp.exe')
    if path_cmd:
        return [path_cmd]

    if not is_frozen():
        return [sys.executable, '-m', 'yt_dlp']

    raise FileNotFoundError(
        "yt-dlp introuvable : place 'yt-dlp.exe' à côté de l'exécutable ou installe-le sur le PATH."
    )
