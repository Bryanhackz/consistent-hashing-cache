# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Consistent hash ring with virtual nodes. O(log N) lookup, ~1/N remap."""

from __future__ import annotations

import bisect
import hashlib


class HashRing:
    """Maps keys to nodes. Virtual nodes provide uniform distribution."""

    def __init__(self, vnodes: int = 150) -> None:
        self.vnodes = vnodes
        self.ring: list[tuple[int, str]] = []
        self.nodes: set[str] = set()

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)

    def add_node(self, node_id: str) -> None:
        if node_id in self.nodes:
            return
        self.nodes.add(node_id)
        for i in range(self.vnodes):
            vnode_key = f"{node_id}:{i}"
            h = self._hash(vnode_key)
            bisect.insort(self.ring, (h, node_id))

    def remove_node(self, node_id: str) -> None:
        if node_id not in self.nodes:
            return
        self.nodes.remove(node_id)
        self.ring = [(h, n) for (h, n) in self.ring if n != node_id]

    def get_node(self, key: str) -> str | None:
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect_right(self.ring, (h, ""))
        if idx == len(self.ring):
            idx = 0
        return self.ring[idx][1]