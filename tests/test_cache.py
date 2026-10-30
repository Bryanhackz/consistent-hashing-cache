# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Tests for cache operations: TTL and LRU."""

import unittest
import sqlite3
from unittest import mock
from src.cache import put, get, delete
from src.config import Config
from pathlib import Path


def _cfg():
    # max 3 entries
    return Config("h", 1, "dev", Path("/tmp"), 10, 3, 1024, 8, 1)


class TestCache(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            "CREATE TABLE cache_entries (key TEXT PRIMARY KEY, value TEXT, expires_at INTEGER, last_accessed INTEGER)"
        )

    def test_ttl(self):
        with mock.patch("src.cache.time.time", return_value=1000):
            put(self.conn, _cfg(), "k1", "v1", ttl_sec=10)
            self.assertEqual(get(self.conn, "k1"), "v1")
        with mock.patch("src.cache.time.time", return_value=1020):
            self.assertIsNone(get(self.conn, "k1"))

    def test_lru_eviction(self):
        cfg = _cfg()
        # Add 3 entries at distinct times so LRU knows exactly which is oldest
        with mock.patch("src.cache.time.time", return_value=1000):
            put(self.conn, cfg, "k1", "v1", None)
        with mock.patch("src.cache.time.time", return_value=1001):
            put(self.conn, cfg, "k2", "v2", None)
        with mock.patch("src.cache.time.time", return_value=1002):
            put(self.conn, cfg, "k3", "v3", None)
            
        # Access k1, making k2 the least recently used
        with mock.patch("src.cache.time.time", return_value=1003):
            get(self.conn, "k1")
            
        # Add k4, exceeds limit (3), must evict k2
        with mock.patch("src.cache.time.time", return_value=1004):
            put(self.conn, cfg, "k4", "v4", None)
            
        self.assertIsNotNone(get(self.conn, "k1"), "k1 should survive")
        self.assertIsNone(get(self.conn, "k2"), "k2 should be evicted")
        self.assertIsNotNone(get(self.conn, "k3"), "k3 should survive")


if __name__ == "__main__":
    unittest.main()