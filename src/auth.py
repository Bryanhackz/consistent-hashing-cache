# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""API-key auth: scrypt hashing, constant-time verify."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
import time

from src.config import Config

KEY_LEN = 43
PREFIX_LEN = 8


def hash_key(cfg: Config, key: str, salt: bytes) -> bytes:
    return hashlib.scrypt(
        key.encode("utf-8"), salt=salt,
        n=cfg.scrypt_n, r=cfg.scrypt_r, p=cfg.scrypt_p, dklen=32
    )


def issue_key(conn: sqlite3.Connection, cfg: Config, label: str, role: str) -> str:
    plaintext = secrets.token_urlsafe(32)
    prefix = plaintext[:PREFIX_LEN]
    salt = secrets.token_bytes(16)
    digest = hash_key(cfg, plaintext, salt)
    conn.execute(
        "INSERT INTO api_keys(label, role, key_prefix, key_hash, key_salt) VALUES(?,?,?,?,?)",
        (label, role, prefix, digest, salt)
    )
    return plaintext


def verify_key(conn: sqlite3.Connection, cfg: Config, key: str) -> str | None:
    if not isinstance(key, str) or len(key) != KEY_LEN:
        return None
    prefix = key[:PREFIX_LEN]
    row = conn.execute(
        "SELECT role, key_hash, key_salt FROM api_keys WHERE key_prefix=?", (prefix,)
    ).fetchone()
    if not row:
        return None
    candidate = hash_key(cfg, key, bytes(row["key_salt"]))
    if hmac.compare_digest(candidate, bytes(row["key_hash"])):
        return str(row["role"])
    return None