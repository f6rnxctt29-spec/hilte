from fastapi import APIRouter
from ..db import get_conn

router = APIRouter(prefix='/audit_logs', tags=['audit_logs'])

@router.get('', response_model=list)
def list_audit_logs(limit: int = 50, target_table: str = None, target_id: str = None):
    with get_conn() as conn:
        if target_table and target_id:
            rows = conn.execute(
                "select id, actor, action, target_table, target_id, meta, ts from audit_logs where target_table=%s and target_id=%s order by ts desc limit %s",
                (target_table, target_id, limit)
            ).fetchall()
        elif target_table:
            rows = conn.execute(
                "select id, actor, action, target_table, target_id, meta, ts from audit_logs where target_table=%s order by ts desc limit %s",
                (target_table, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "select id, actor, action, target_table, target_id, meta, ts from audit_logs order by ts desc limit %s",
                (limit,)
            ).fetchall()
    return [dict(r) for r in rows]

@router.post('', response_model=dict)
def create_audit_log(payload: dict):
    with get_conn() as conn:
        row = conn.execute(
            "insert into audit_logs (actor, action, target_table, target_id, meta) values (%s,%s,%s,%s,%s) returning id, actor, action, target_table, target_id, meta, ts",
            (
                payload.get('actor','system'),
                payload.get('action'),
                payload.get('target_table'),
                payload.get('target_id'),
                payload.get('meta','{}')
            ),
        ).fetchone()
        conn.commit()
    return dict(row)
