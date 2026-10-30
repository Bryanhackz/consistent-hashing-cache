# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Cache operations route handlers: GET, PUT, DELETE."""

from __future__ import annotations

import contextlib
from src import cache
from src.config import Config
from src.db import connect, transaction
from src.router import Router
from src.validators import ValidationError, validate_key, validate_value
from src.routes.utils import json_response, error_response, read_json


def handle_cache(environ, start_response, method: str, path: str, cfg: Config, router: Router):
    """Route a cache operation to the correct node DB."""
    key = path.replace("/cache/", "", 1)
    try:
        validate_key(key)
    except ValidationError as e:
        return error_response(start_response, "400 Bad Request", "invalid", str(e))

    db_path = router.get_db_path(key)
    if not db_path:
        return error_response(start_response, "503 Service Unavailable", "no_nodes", "no nodes active")

    with contextlib.closing(connect(db_path)) as node_conn:
        if method == "GET":
            val = cache.get(node_conn, key)
            if val is None:
                return error_response(start_response, "404 Not Found", "miss", "key not found")
            return json_response(start_response, "200 OK", {"key": key, "value": val})

        elif method == "PUT":
            try:
                payload = read_json(environ)
                val = validate_value(payload.get("value"))
                ttl = payload.get("ttl")
            except Exception as e:
                return error_response(start_response, "400 Bad Request", "invalid", str(e))

            with transaction(node_conn):
                cache.put(node_conn, cfg, key, val, ttl)
            return json_response(start_response, "201 Created", {"key": key, "status": "stored"})

        elif method == "DELETE":
            with transaction(node_conn):
                ok = cache.delete(node_conn, key)
            return json_response(start_response, "200 OK", {"deleted": ok})