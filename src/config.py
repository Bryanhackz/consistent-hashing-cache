# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Central configuration. Parses env vars with validation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _int_env(name: str, default: int, minimum: int = 1) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        val = int(raw)
    except ValueError:
        raise ValueError(f"{name} must be int") from None
    if val < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return val


@dataclass(frozen=True)
class Config:
    """Immutable cache configuration."""

    host: str
    port: int
    env: str
    data_dir: Path
    vnodes: int
    max_entries: int
    scrypt_n: int
    scrypt_r: int
    scrypt_p: int

    @property
    def meta_db_path(self) -> Path:
        return self.data_dir / "meta.db"


def load_config() -> Config:
    return Config(
        host=os.environ.get("SMB_HOST", "127.0.0.1"),
        port=_int_env("SMB_PORT", 8081),
        env=os.environ.get("SMB_ENV", "dev"),
        data_dir=Path(os.environ.get("SMB_DATA_DIR", "./data")),
        vnodes=_int_env("SMB_VNODES", 150),
        max_entries=_int_env("SMB_MAX_ENTRIES_PER_NODE", 1000),
        scrypt_n=_int_env("SMB_SCRYPT_N", 16384),
        scrypt_r=_int_env("SMB_SCRYPT_R", 8),
        scrypt_p=_int_env("SMB_SCRYPT_P", 1),
    )