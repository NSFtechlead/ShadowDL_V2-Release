import json
import tempfile
import unittest
from pathlib import Path

from shadowdl.config import MODES, load_config, normalize_config, save_config


class ConfigTests(unittest.TestCase):
    def test_normalize_config_repairs_unknown_values(self):
        cfg = normalize_config(
            {
                "mode": "ancien mode",
                "browser": "netscape",
                "playlist": 1,
                "safe_mode": 0,
                "use_browser_cookies": "yes",
                "outdir": "  C:/Temp  ",
            }
        )

        self.assertEqual(cfg["mode"], MODES[0])
        self.assertEqual(cfg["browser"], "chrome")
        self.assertTrue(cfg["playlist"])
        self.assertFalse(cfg["safe_mode"])
        self.assertTrue(cfg["use_browser_cookies"])
        self.assertEqual(cfg["outdir"], "C:/Temp")

    def test_load_config_reads_primary_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = root / "ShadowDL" / "config.json"
            primary.parent.mkdir(parents=True)
            primary.write_text(json.dumps({"mode": MODES[1], "browser": "firefox"}), encoding="utf-8")

            cfg = load_config(primary)

        self.assertEqual(cfg["mode"], MODES[1])
        self.assertEqual(cfg["browser"], "firefox")

    def test_save_config_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "config.json"
            save_config({"mode": MODES[1], "outdir": "X"}, path)
            cfg = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(cfg["mode"], MODES[1])
        self.assertEqual(cfg["outdir"], "X")


if __name__ == "__main__":
    unittest.main()
