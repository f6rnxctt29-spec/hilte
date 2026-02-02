from fastapi import APIRouter
from typing import Optional
from ..db import get_conn

router = APIRouter(prefix='/audit_logs', tags=['audit_logs'])

@router.get('', response_model=list[dict])
def list_audit_logs(limit: int = 50, target_table: Optional[str] = None, target_id: Optional[str] = None):
    where = []
    args: list = []
    if target_table:
        where.append('target_table=%s')
        args.append(target_table)
    if target_id:
        where.append('target_id=%s')
        args.append(target_id)

    sql = "select id, actor, action, target_table, target_id, meta, ts from audit_logs"
    if where:
        sql += ' where ' + ' and '.join(where)
    sql += ' order by ts desc limit %s'
    args.append(limit)

    with get_conn() as conn:
        rows = conn.execute(sql, tuple(args)).fetchall()

    return [dict(r) for r in rows]
