from __future__ import annotations

from typing import Any
from psycopg.types.json import Json


def j(v: Any):
    """Wrap python dict/list for json/jsonb columns."""
    return Json(v)
