# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Tests for consistent hashing: balance and remap ratio."""
import unittest
from src.hash_ring import HashRing

class TestHashRing(unittest.TestCase):
    def test_remap_ratio(self):
        ring = HashRing(vnodes=150)
        for i in range(4):
            ring.add_node(f"node_{i}")
        
        keys = [f"key_{i}" for i in range(1000)]
        orig_map = {k: ring.get_node(k) for k in keys}
        
        ring.add_node("node_4")
        new_map = {k: ring.get_node(k) for k in keys}
        
        remapped = sum(1 for k in keys if orig_map[k] != new_map[k])
        ratio = remapped / len(keys)
        
        # 5 nodes total, consistent hashing should remap ~20% (1/5).
        # We assert < 30% to allow for statistical variance.
        self.assertLess(ratio, 0.30, "Consistent hash should not remap >30% of keys")

if __name__ == "__main__":
    unittest.main()