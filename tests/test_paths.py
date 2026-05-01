import tempfile
import unittest
from pathlib import Path
from unittest import mock

from shadowdl.paths import local_ffmpeg_bin_dir, runtime_cache_dir, ytdlp_cmd_base


class PathTests(unittest.TestCase):
    def test_local_ffmpeg_detection_requires_ffmpeg_and_ffprobe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / 'ffmpeg' / 'bin'
            bin_dir.mkdir(parents=True)
            (bin_dir / 'ffmpeg.exe').write_text('', encoding='utf-8')
            self.assertIsNone(local_ffmpeg_bin_dir(root))

            (bin_dir / 'ffprobe.exe').write_text('', encoding='utf-8')
            self.assertEqual(local_ffmpeg_bin_dir(root), bin_dir)

    def test_ytdlp_prefers_local_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binary = root / 'yt-dlp.exe'
            binary.write_text('', encoding='utf-8')

            self.assertEqual(ytdlp_cmd_base(root), [str(binary)])

    def test_source_mode_can_use_runtime_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root / '.runtime'
            runtime.mkdir()
            ytdlp = runtime / 'yt-dlp.exe'
            ytdlp.write_text('', encoding='utf-8')
            ffmpeg_bin = runtime / 'ffmpeg' / 'bin'
            ffmpeg_bin.mkdir(parents=True)
            (ffmpeg_bin / 'ffmpeg.exe').write_text('', encoding='utf-8')
            (ffmpeg_bin / 'ffprobe.exe').write_text('', encoding='utf-8')

            with mock.patch('shadowdl.paths.project_root', return_value=root):
                self.assertEqual(ytdlp_cmd_base(), [str(ytdlp)])
                self.assertEqual(runtime_cache_dir(), runtime)
                self.assertEqual(local_ffmpeg_bin_dir(), ffmpeg_bin)

    def test_frozen_layout_uses_pyinstaller_internal_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            internal = root / '_internal'
            internal.mkdir()
            ytdlp = internal / 'yt-dlp.exe'
            ytdlp.write_text('', encoding='utf-8')
            ffmpeg_bin = internal / 'ffmpeg' / 'bin'
            ffmpeg_bin.mkdir(parents=True)
            (ffmpeg_bin / 'ffmpeg.exe').write_text('', encoding='utf-8')
            (ffmpeg_bin / 'ffprobe.exe').write_text('', encoding='utf-8')

            with (
                mock.patch('sys.frozen', True, create=True),
                mock.patch('sys._MEIPASS', str(internal), create=True),
                mock.patch('sys.executable', str(root / 'ShadowDL_V2.3.exe')),
            ):
                self.assertEqual(Path(ytdlp_cmd_base()[0]).resolve(), ytdlp.resolve())
                self.assertEqual(local_ffmpeg_bin_dir(), ffmpeg_bin.resolve())


if __name__ == '__main__':
    unittest.main()
