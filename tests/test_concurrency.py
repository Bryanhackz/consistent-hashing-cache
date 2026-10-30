# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Concurrency test: parallel PUTs to the same node."""
import tempfile, threading, unittest
from contextlib import closing
from pathlib import Path
from src.cache import put
from src.config import Config
from src.db import connect, init_db, init_node_db


class TestConcurrency(unittest.TestCase):
    def test_parallel_puts(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
            cfg = Config("h", 1, "dev", Path(td), 10, 1000, 1024, 8, 1)
            init_db(cfg)
            
            # Create node manually to avoid needing the Router in this test
            with connect(cfg.meta_db_path) as c:
                c.execute("INSERT INTO nodes(id) VALUES('n1')")
                
            init_node_db(cfg, "n1")
            db_path = cfg.data_dir / "node_n1.db"

            def worker(i):
                with closing(connect(db_path)) as conn:
                    with conn:
                        put(conn, cfg, f"key_{i}", "val", None)

            threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            with closing(connect(db_path)) as conn:
                count = conn.execute("SELECT COUNT(*) FROM cache_entries").fetchone()[0]
            self.assertEqual(count, 50)


if __name__ == "__main__":
    unittest.main()