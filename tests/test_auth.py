# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Tests for scrypt API keys."""
import unittest, sqlite3
from src.auth import issue_key, verify_key, KEY_LEN
from src.config import Config
from pathlib import Path

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.cfg = Config("h", 1, "dev", Path("/tmp"), 10, 100, 1024, 8, 1)
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("CREATE TABLE api_keys (label TEXT, role TEXT, key_prefix TEXT UNIQUE, key_hash BLOB, key_salt BLOB)")

    def test_roundtrip(self):
        key = issue_key(self.conn, self.cfg, "admin", "admin")
        self.assertEqual(len(key), KEY_LEN)
        self.assertEqual(verify_key(self.conn, self.cfg, key), "admin")
        self.assertIsNone(verify_key(self.conn, self.cfg, "wrong"))

if __name__ == "__main__":
    unittest.main()