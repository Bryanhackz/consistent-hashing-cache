# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""WSGI entry point. Boots the broker with initialized DBs and router."""

from __future__ import annotations

import logging
import sys
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer, make_server

from src.app import build_app
from src.config import load_config
from src.db import init_db
from src.router import Router


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    """Threaded server; required for concurrent cache hits/misses."""
    daemon_threads = True
    allow_reuse_address = True


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stderr,
    )


def main() -> int:
    cfg = load_config()
    _configure_logging("INFO")
    init_db(cfg)
    
    router = Router(cfg)
    app = build_app(cfg, router)
    
    with make_server(cfg.host, cfg.port, app, server_class=ThreadingWSGIServer) as srv:
        logging.info("serving http://%s:%s env=%s", cfg.host, cfg.port, cfg.env)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            logging.info("shutdown requested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())