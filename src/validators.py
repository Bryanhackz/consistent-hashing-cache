# © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
"""Input validation for keys, values, and node IDs."""

from __future__ import annotations

import re


class ValidationError(ValueError):
    """Raised on bad input."""


_NODE_ID_RE = re.compile(r"^[a-z0-9_-]{1,32}$")
_KEY_RE = re.compile(r"^[a-zA-Z0-9_.-]{1,256}$")


def validate_node_id(node_id: object) -> str:
    if not isinstance(node_id, str) or not _NODE_ID_RE.match(node_id):
        raise ValidationError("node_id must match ^[a-z0-9_-]{1,32}$")
    return node_id


def validate_key(key: object) -> str:
    if not isinstance(key, str) or not _KEY_RE.match(key):
        raise ValidationError("key must match ^[a-zA-Z0-9_.-]{1,256}$")
    return key


def validate_value(value: object) -> str:
    if not isinstance(value, str):
        raise ValidationError("value must be a string")
    if len(value.encode("utf-8")) > 64 * 1024:
        raise ValidationError("value exceeds 64KiB")
    return value