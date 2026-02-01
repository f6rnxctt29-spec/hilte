from fastapi import APIRouter
from ..db import get_conn

router = APIRouter(prefix='/audit_logs', tags=['audit_logs'])

@router.get('', response_model=list)
def list_audit_logs(limit: int = 50, target_table: str = None, target_id: str = None):
    with get_conn() as conn:
        if target_table and target_id:
            sql = "select json_build_object('id', id, 'actor', actor, 'action', action, 'target_table', target_table, 'target_id', target_id, 'meta', meta, 'ts', ts)::text as obj from audit_logs where target_table=%s and target_id=%s order by ts desc limit %s"
            rows = conn.execute(sql, (target_table, target_id, limit)).fetchall()
        elif target_table:
            sql = "select json_build_object('id', id, 'actor', actor, 'action', action, 'target_table', target_table, 'target_id', target_id, 'meta', meta, 'ts', ts)::text as obj from audit_logs where target_table=%s order by ts desc limit %s"
            rows = conn.execute(sql, (target_table, limit)).fetchall()
        else:
            sql = "select json_build_object('id', id, 'actor', actor, 'action', action, 'target_table', target_table, 'target_id', target_id, 'meta', meta, 'ts', ts)::text as obj from audit_logs order by ts desc limit %s"
            rows = conn.execute(sql, (limit,)).fetchall()
    import json
    result = []
    for r in rows:
        try:
            result.append(json.loads(r[0]))
        except Exception:
            result.append({})
    return result

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
