# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Tests for config parsing."""
import os, unittest
from unittest import mock
from src.config import load_config

class TestConfig(unittest.TestCase):
    def test_defaults(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.port, 8081)
        self.assertEqual(cfg.vnodes, 150)

    def test_overrides(self):
        with mock.patch.dict(os.environ, {"SMB_PORT": "9000", "SMB_VNODES": "10"}, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.port, 9000)
        self.assertEqual(cfg.vnodes, 10)

if __name__ == "__main__":
    unittest.main()