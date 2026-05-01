import json
import os
from pathlib import Path

from shadowdl import APP_NAME


MODES = ("Complet (meilleure vidéo + audio)", "Audio (MP3)")
BROWSERS = ("chrome", "edge", "firefox", "brave", "opera", "opera-gx")


def appdata_dir() -> Path:
    return Path(os.getenv("APPDATA") or Path.home())


def default_outdir() -> str:
    downloads = Path.home() / "Downloads"
    return str(downloads) if downloads.is_dir() else ""


DEFAULT_CONFIG = {
    "outdir": default_outdir(),
    "mode": MODES[0],
    "playlist": True,
    "safe_mode": False,
    "browser": "chrome",
    "use_browser_cookies": False,
}


def config_path(appdata: Path | None = None) -> Path:
    return (appdata or appdata_dir()) / APP_NAME / "config.json"


def normalize_config(data: dict | None) -> dict:
    cfg = DEFAULT_CONFIG.copy()
    if isinstance(data, dict):
        cfg.update({key: data[key] for key in DEFAULT_CONFIG if key in data})

    if cfg["mode"] not in MODES:
        cfg["mode"] = MODES[0]
    if cfg["browser"] not in BROWSERS:
        cfg["browser"] = "chrome"

    cfg["playlist"] = bool(cfg["playlist"])
    cfg["safe_mode"] = bool(cfg["safe_mode"])
    cfg["use_browser_cookies"] = bool(cfg["use_browser_cookies"])
    cfg["outdir"] = str(cfg["outdir"]).strip()
    return cfg


def read_json(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def load_config(path: Path | None = None) -> dict:
    primary = path or config_path()
    return normalize_config(read_json(primary))


def save_config(cfg: dict, path: Path | None = None) -> None:
    target = path or config_path()
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as handle:
            json.dump(normalize_config(cfg), handle, ensure_ascii=False, indent=2)
    except OSError:
        pass
