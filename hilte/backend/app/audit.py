from __future__ import annotations

from uuid import UUID
from typing import Any, Optional
from psycopg.types.json import Json


def log_action(
    conn,
    *,
    actor: str,
    action: str,
    target_table: Optional[str] = None,
    target_id: Optional[UUID] = None,
    meta: Optional[dict[str, Any]] = None,
) -> None:
    conn.execute(
        """
        insert into audit_logs (actor, action, target_table, target_id, meta)
        values (%s,%s,%s,%s,%s)
        """,
        (
            actor,
            action,
            target_table,
            str(target_id) if target_id else None,
            Json(meta or {}),
        ),
    )
