# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Database layer: meta.db (nodes, auth, ratelimit) + node_X.db (cache)."""

from __future__ import annotations

import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Iterator

from src.config import Config

META_SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'active'
);
CREATE TABLE IF NOT EXISTS api_keys (
    label TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    key_prefix TEXT NOT NULL UNIQUE,
    key_hash BLOB NOT NULL,
    key_salt BLOB NOT NULL
);
CREATE TABLE IF NOT EXISTS rate_limit_buckets (
    scope TEXT NOT NULL,
    identity TEXT NOT NULL,
    window_start INTEGER NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (scope, identity, window_start)
);
"""

NODE_SCHEMA = """
CREATE TABLE IF NOT EXISTS cache_entries (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    expires_at INTEGER,
    last_accessed INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_lru ON cache_entries(last_accessed);
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=5.0, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db(cfg: Config) -> None:
    """Initialize meta DB."""
    with closing(connect(cfg.meta_db_path)) as conn:
        conn.executescript(META_SCHEMA)


def init_node_db(cfg: Config, node_id: str) -> None:
    """Initialize a specific node's SQLite file."""
    path = cfg.data_dir / f"node_{node_id}.db"
    with closing(connect(path)) as conn:
        conn.executescript(NODE_SCHEMA)


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise