import unittest

from shadowdl.command import DownloadOptions, build_ytdlp_command
from shadowdl.config import MODES


class BuildYtDlpCommandTests(unittest.TestCase):
    def test_video_command_uses_local_ffmpeg_and_single_concurrency_value(self):
        cmd = build_ytdlp_command(
            DownloadOptions(
                url="https://example.com/video",
                outdir=r"C:\Downloads",
                mode=MODES[0],
                allow_playlist=False,
                ytdlp_base=["yt-dlp"],
                ffmpeg_dir=r"C:\Tools\ffmpeg\bin",
            )
        )

        self.assertEqual(cmd[0], "yt-dlp")
        self.assertIn("--ffmpeg-location", cmd)
        self.assertIn(r"C:\Tools\ffmpeg\bin", cmd)
        self.assertEqual(cmd.count("-N"), 1)
        self.assertEqual(cmd[cmd.index("-N") + 1], "8")
        self.assertIn("--no-playlist", cmd)
        self.assertIn("%(title)s [%(id)s].%(ext)s", cmd)

    def test_safe_mode_replaces_fast_retry_settings(self):
        cmd = build_ytdlp_command(
            DownloadOptions(
                url="https://example.com/video",
                outdir=r"C:\Downloads",
                mode=MODES[0],
                allow_playlist=True,
                safe_mode=True,
                ytdlp_base=["yt-dlp"],
                ffmpeg_dir=r"C:\Tools\ffmpeg\bin",
            )
        )

        self.assertEqual(cmd.count("-N"), 1)
        self.assertEqual(cmd[cmd.index("-N") + 1], "1")
        self.assertIn("--downloader", cmd)
        self.assertIn("ffmpeg", cmd)
        self.assertIn("--yes-playlist", cmd)
        self.assertTrue(any("%(playlist_index|0)03d" in part for part in cmd))

    def test_audio_command_extracts_mp3_with_metadata(self):
        cmd = build_ytdlp_command(
            DownloadOptions(
                url="https://example.com/video",
                outdir=r"C:\Downloads",
                mode=MODES[1],
                allow_playlist=False,
                ytdlp_base=["yt-dlp"],
                ffmpeg_dir=None,
            )
        )

        self.assertIn("-x", cmd)
        self.assertIn("--audio-format", cmd)
        self.assertIn("mp3", cmd)
        self.assertIn("--embed-metadata", cmd)


if __name__ == "__main__":
    unittest.main()
