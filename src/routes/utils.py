# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Shared WSGI response helpers."""

from __future__ import annotations

import json
import logging
import uuid

log = logging.getLogger("chc.routes")

SECURITY_HEADERS = [
    ("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'none'"),
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "no-referrer"),
    ("Cache-Control", "no-store"),
]


def json_response(start_response, status: str, payload: dict, extra: list | None = None):
    """Emit a JSON response with security headers."""
    body = json.dumps(payload).encode("utf-8")
    headers = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(body))),
    ] + SECURITY_HEADERS
    if extra:
        headers += extra
    start_response(status, headers)
    return [body]


def error_response(start_response, status: str, code: str, msg: str):
    """Emit a uniform error envelope."""
    log_id = uuid.uuid4().hex[:8]
    log.warning("err id=%s code=%s msg=%s", log_id, code, msg)
    return json_response(start_response, status, {"code": code, "message": msg, "log_id": log_id})


def read_json(environ: dict) -> dict:
    """Parse a bounded JSON object from the WSGI input stream."""
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        raise ValueError("invalid Content-Length") from None
    if length <= 0:
        raise ValueError("empty body")
    if length > 128 * 1024:
        raise ValueError("body too large")
    raw = environ["wsgi.input"].read(length)
    return json.loads(raw.decode("utf-8"))