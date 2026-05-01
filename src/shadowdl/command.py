import shlex
from dataclasses import dataclass
from pathlib import Path

from shadowdl.config import MODES
from shadowdl.paths import local_ffmpeg_bin_dir, ytdlp_cmd_base


@dataclass(frozen=True)
class DownloadOptions:
    url: str
    outdir: str
    mode: str
    allow_playlist: bool
    use_browser_cookies: bool = False
    browser: str = "chrome"
    safe_mode: bool = False
    ytdlp_base: list[str] | None = None
    ffmpeg_dir: str | Path | None = None


def format_command(cmd: list[str]) -> str:
    try:
        return shlex.join(cmd)
    except Exception:
        return " ".join(f'"{part}"' if " " in part else part for part in cmd)


def build_ytdlp_command(options: DownloadOptions) -> list[str]:
    cmd = list(options.ytdlp_base or ytdlp_cmd_base())
    cmd += [
        "--newline",
        "--color",
        "never",
        "--windows-filenames",
        "--trim-filenames",
        "180",
        "--progress-delta",
        "0.5",
    ]

    if options.use_browser_cookies:
        cmd += ["--cookies-from-browser", options.browser.strip() or "chrome"]

    ffmpeg_dir = options.ffmpeg_dir
    if ffmpeg_dir is None:
        ffmpeg_dir = local_ffmpeg_bin_dir()
    if ffmpeg_dir:
        cmd += ["--ffmpeg-location", str(ffmpeg_dir)]

    if options.safe_mode:
        cmd += [
            "-N",
            "1",
            "--retries",
            "50",
            "--fragment-retries",
            "50",
            "--retry-sleep",
            "exp=2:30",
            "--retry-sleep",
            "fragment:exp=2:30",
            "--http-chunk-size",
            "1M",
        ]
        if ffmpeg_dir:
            cmd += [
                "--downloader",
                "ffmpeg",
                "--downloader-args",
                "ffmpeg:-reconnect 1 -reconnect_streamed 1 -reconnect_on_network_error 1 -rw_timeout 30000000",
            ]
    else:
        cmd += [
            "-N",
            "8",
            "--retries",
            "20",
            "--fragment-retries",
            "20",
            "--retry-sleep",
            "exp=1:20",
            "--retry-sleep",
            "fragment:exp=1:20",
        ]

    if options.mode == MODES[0]:
        cmd += [
            "-f",
            "bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/b",
            "-S",
            "res,fps,ext:mp4:m4a",
        ]
    else:
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0", "--embed-metadata"]

    if options.allow_playlist:
        cmd += ["--yes-playlist"]
        out_tmpl = "%(playlist_title|Playlist)s/%(playlist_index|0)03d - %(title)s [%(id)s].%(ext)s"
    else:
        cmd += ["--no-playlist"]
        out_tmpl = "%(title)s [%(id)s].%(ext)s"

    cmd += ["-P", options.outdir, "-o", out_tmpl, options.url]
    return cmd
