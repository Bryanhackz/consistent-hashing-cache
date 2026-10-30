# consistent-hashing-cache

A distributed cache that partitions keys across simulated nodes using a **consistent hash ring** with virtual nodes. Written exclusively in Python 3.11+ stdlib.

## Problem / Solution / Impact
- **Problem:** Simple modulo hashing (`hash(key) % N`) causes massive key remapping when nodes are added or removed (~80% of keys move), destroying cache hit rates.
- **Solution:** A consistent hash ring maps both keys and nodes to the same circular space. Adding a node only remaps `~1/N` of keys (e.g., adding the 5th node remaps only 20%).
- **Impact:** Backend teams can scale caching horizontally without cold-starting the entire cache.

## Architecture
```text
consistent-hashing-cache/
├── run.py
├── src/
│   ├── app.py        # WSGI dispatcher, security headers
│   ├── cache.py      # GET/PUT/DELETE with TTL + LRU eviction
│   ├── db.py         # meta.db (ring state) + node_X.db (cache data)
│   ├── hash_ring.py  # Bisect-based ring, MD5 virtual nodes
│   ├── router.py     # Wraps hash ring, maps keys to node DBs
│   └── ...
├── templates/admin.html
├── static/admin.{js,css}
└── tests/