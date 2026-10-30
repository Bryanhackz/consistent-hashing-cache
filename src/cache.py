# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Cache operations: GET, PUT, DELETE. Enforces TTL and LRU bounds."""

from __future__ import annotations

import sqlite3
import time

from src.config import Config


def get(conn: sqlite3.Connection, key: str) -> str | None:
    now = int(time.time())
    row = conn.execute(
        "SELECT value, expires_at FROM cache_entries WHERE key=?", (key,)
    ).fetchone()
    if not row:
        return None
    if row["expires_at"] and row["expires_at"] < now:
        conn.execute("DELETE FROM cache_entries WHERE key=?", (key,))
        return None
    conn.execute("UPDATE cache_entries SET last_accessed=? WHERE key=?", (now, key))
    return str(row["value"])


def put(conn: sqlite3.Connection, cfg: Config, key: str, value: str, ttl_sec: int | None) -> None:
    now = int(time.time())
    expires = now + ttl_sec if ttl_sec else None
    conn.execute(
        "INSERT OR REPLACE INTO cache_entries (key, value, expires_at, last_accessed) VALUES (?,?,?,?)",
        (key, value, expires, now)
    )
    count = conn.execute("SELECT COUNT(*) FROM cache_entries").fetchone()[0]
    if count > cfg.max_entries:
        to_evict = count - cfg.max_entries
        conn.execute(
            "DELETE FROM cache_entries WHERE key IN (SELECT key FROM cache_entries ORDER BY last_accessed ASC LIMIT ?)",
            (to_evict,)
        )


def delete(conn: sqlite3.Connection, key: str) -> bool:
    cur = conn.execute("DELETE FROM cache_entries WHERE key=?", (key,))
    return cur.rowcount > 0