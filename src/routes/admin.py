# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Admin route handlers: node management and stats."""

from __future__ import annotations

import contextlib
from src.config import Config
from src.db import connect
from src.router import Router
from src.validators import validate_node_id
from src.routes.utils import json_response, error_response, read_json


def handle_add_node(environ, start_response, cfg: Config, router: Router):
    """Add a node to the hash ring and create its SQLite DB."""
    try:
        payload = read_json(environ)
        node_id = validate_node_id(payload.get("id"))
    except Exception as e:
        return error_response(start_response, "400 Bad Request", "invalid", str(e))

    router.add_node(node_id)
    return json_response(start_response, "201 Created", {"status": "node added", "id": node_id})


def handle_stats(environ, start_response, cfg: Config):
    """Return the number of keys currently stored in each active node."""
    stats = {}
    with connect(cfg.meta_db_path) as meta:
        nodes = meta.execute("SELECT id FROM nodes WHERE status='active'").fetchall()
    for n in nodes:
        db_path = cfg.data_dir / f"node_{n['id']}.db"
        with contextlib.closing(connect(db_path)) as c:
            count = c.execute("SELECT COUNT(*) FROM cache_entries").fetchone()[0]
        stats[n["id"]] = count
    return json_response(start_response, "200 OK", {"nodes": stats})