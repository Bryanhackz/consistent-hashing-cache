# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Routes keys to node DB paths using the hash ring."""

from __future__ import annotations

from pathlib import Path
from src.config import Config
from src.db import connect, init_node_db
from src.hash_ring import HashRing


class Router:
    """Holds the HashRing state and resolves node DB paths."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.ring = HashRing(vnodes=cfg.vnodes)
        self._load_nodes()

    def _load_nodes(self) -> None:
        with connect(self.cfg.meta_db_path) as conn:
            rows = conn.execute("SELECT id FROM nodes WHERE status='active'").fetchall()
        for r in rows:
            self.ring.add_node(r["id"])

    def add_node(self, node_id: str) -> None:
        self.ring.add_node(node_id)
        init_node_db(self.cfg, node_id)
        with connect(self.cfg.meta_db_path) as conn:
            conn.execute("INSERT OR IGNORE INTO nodes(id) VALUES(?)", (node_id,))

    def remove_node(self, node_id: str) -> None:
        self.ring.remove_node(node_id)
        with connect(self.cfg.meta_db_path) as conn:
            conn.execute("UPDATE nodes SET status='removed' WHERE id=?", (node_id,))

    def get_db_path(self, key: str) -> Path | None:
        node_id = self.ring.get_node(key)
        if node_id is None:
            return None
        return self.cfg.data_dir / f"node_{node_id}.db"

    def get_node_for_key(self, key: str) -> str | None:
        return self.ring.get_node(key)