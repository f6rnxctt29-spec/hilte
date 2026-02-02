from __future__ import annotations

from typing import Any
from psycopg.types.json import Json


def j(value: Any) -> Json:
    """Wrap Python dict/list primitives for json/jsonb parameters in psycopg."""
    return Json(value)
