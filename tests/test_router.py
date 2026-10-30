# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Tests for key -> node routing."""
import tempfile, unittest
from pathlib import Path
from src.router import Router
from src.config import Config
from src.db import init_db


class TestRouter(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.cfg = Config("h", 1, "dev", Path(self._tmp.name), 10, 100, 1024, 8, 1)
        init_db(self.cfg)
        
        self.router = Router(self.cfg)
        # Add nodes directly to the ring to isolate the test from the DB
        self.router.ring.add_node("n1")
        self.router.ring.add_node("n2")

    def tearDown(self):
        self._tmp.cleanup()

    def test_routing(self):
        n1 = self.router.get_node_for_key("key1")
        n2 = self.router.get_node_for_key("key2")
        self.assertIn(n1, ("n1", "n2"))
        self.assertIn(n2, ("n1", "n2"))
        self.assertIn(n1, self.router.ring.nodes)


if __name__ == "__main__":
    unittest.main()