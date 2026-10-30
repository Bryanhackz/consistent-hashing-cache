# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""WSGI dispatcher, static serving, authentication enforcement."""

from __future__ import annotations

import contextlib
import logging
import mimetypes
from pathlib import Path

from src.config import Config
from src.db import connect, transaction
from src.router import Router
from src.auth import verify_key
from src.ratelimit import check_and_increment
from src.routes.cache_ops import handle_cache
from src.routes.admin import handle_add_node, handle_stats
from src.routes.utils import json_response, error_response, SECURITY_HEADERS

log = logging.getLogger("chc.app")
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def build_app(cfg: Config, router: Router):
    """Return the WSGI application."""

    def app(environ, start_response):
        try:
            return _dispatch(environ, start_response)
        except Exception:
            log.exception("unhandled")
            return error_response(start_response, "500 Internal Server Error", "internal", "error")

    def _dispatch(environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/")

        # Public endpoints
        if path.startswith("/static/") or path.startswith("/templates/"):
            return _static(path, start_response)

        if path == "/health" and method == "GET":
            return json_response(start_response, "200 OK", {"status": "ok"})

        # Authenticated endpoints
        with contextlib.closing(connect(cfg.meta_db_path)) as meta_conn:
            role = _authenticate(environ, cfg, meta_conn)
            if not role:
                return error_response(start_response, "401 Unauthorized", "unauthorized", "invalid api key")

            # Rate limit all authenticated requests per IP
            ip = environ.get("REMOTE_ADDR", "unknown")
            if not check_and_increment(meta_conn, "api", ip, 120): # 120 req/min default
                return error_response(start_response, "429 Too Many Requests", "rate_limited", "too many requests")

            if path.startswith("/cache/") and method in ("GET", "PUT", "DELETE"):
                return handle_cache(environ, start_response, method, path, cfg, router)

            if path == "/admin/nodes" and method == "POST":
                if role != "admin":
                    return error_response(start_response, "403 Forbidden", "forbidden", "admin role required")
                return handle_add_node(environ, start_response, cfg, router)
                
            if path == "/admin/stats" and method == "GET":
                if role != "admin":
                    return error_response(start_response, "403 Forbidden", "forbidden", "admin role required")
                return handle_stats(environ, start_response, cfg)

            return error_response(start_response, "404 Not Found", "not_found", "not found")

    def _authenticate(environ, cfg: Config, conn) -> str | None:
        """Return the role of the provided API key, or None."""
        key = environ.get("HTTP_X_API_KEY")
        if not key:
            return None
        return verify_key(conn, cfg, key)

    def _static(path, start_response):
        rel = path.lstrip("/")
        target = (PROJECT_ROOT / rel).resolve()
        
        if not str(target).startswith(str(PROJECT_ROOT / "static")) and \
           not str(target).startswith(str(PROJECT_ROOT / "templates")):
            return error_response(start_response, "403 Forbidden", "forbidden", "forbidden")
        if not target.is_file():
            return error_response(start_response, "404 Not Found", "not_found", "file not found")
            
        mime, _ = mimetypes.guess_type(str(target))
        body = target.read_bytes()
        start_response("200 OK", [
            ("Content-Type", mime or "application/octet-stream"),
            ("Content-Length", str(len(body)))
        ] + SECURITY_HEADERS)
        return [body]

    return app