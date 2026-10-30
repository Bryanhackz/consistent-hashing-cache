# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Tests for WSGI routing and headers."""
import tempfile, unittest
from pathlib import Path
from src.app import build_app
from src.config import Config
from src.db import init_db
from src.router import Router


def _cfg(td):
    return Config("h", 1, "dev", Path(td), 10, 100, 1024, 8, 1)


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.cfg = _cfg(self._tmp.name)
        init_db(self.cfg)
        
        self.router = Router(self.cfg)
        self.router.add_node("n1")
        self.app = build_app(self.cfg, self.router)

    def tearDown(self):
        self._tmp.cleanup()

    def test_health(self):
        env = {"REQUEST_METHOD": "GET", "PATH_INFO": "/health"}
        cap = {}
        self.app(env, lambda s, h: cap.update({"status": s, "headers": dict(h)}))
        self.assertEqual(cap["status"], "200 OK")
        self.assertIn("Content-Security-Policy", cap["headers"])


if __name__ == "__main__":
    unittest.main()