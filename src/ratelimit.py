# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Fixed-window rate limiter persisted in meta.db."""

from __future__ import annotations

import sqlite3
import time

WINDOW_SEC = 60


def check_and_increment(conn: sqlite3.Connection, scope: str, identity: str, limit: int) -> bool:
    now = int(time.time())
    window = now - (now % WINDOW_SEC)
    row = conn.execute(
        "SELECT count FROM rate_limit_buckets WHERE scope=? AND identity=? AND window_start=?",
        (scope, identity, window)
    ).fetchone()
    current = int(row["count"]) if row else 0
    if current >= limit:
        return False
    if row:
        conn.execute("UPDATE rate_limit_buckets SET count=count+1 WHERE scope=? AND identity=? AND window_start=?",
                     (scope, identity, window))
    else:
        conn.execute("INSERT INTO rate_limit_buckets(scope, identity, window_start, count) VALUES(?,?,?,1)",
                     (scope, identity, window))
    return True