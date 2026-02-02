from fastapi import APIRouter, HTTPException, Header
from uuid import UUID
from ..db import get_conn
from ..audit import log_action

router = APIRouter(prefix='/incidents', tags=['incidents'])

@router.get('', response_model=list[dict])
def list_incidents(limit: int = 50):
    with get_conn() as conn:
        rows = conn.execute(
            "select id, order_id, reporter_id, severity, status, text, resolution, created_at, updated_at from incidents order by created_at desc limit %s",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]

@router.post('', response_model=dict)
def create_incident(payload: dict, x_actor: str = Header(default='system')):
    with get_conn() as conn:
        row = conn.execute(
            "insert into incidents (order_id, reporter_id, severity, status, text, resolution) values (%s,%s,%s,%s,%s,%s) returning id, order_id, reporter_id, severity, status, text, resolution, created_at, updated_at",
            (
                payload.get('order_id'),
                payload.get('reporter_id'),
                payload.get('severity', 'low'),
                payload.get('status', 'open'),
                payload.get('text'),
                payload.get('resolution'),
            ),
        ).fetchone()
        log_action(conn, actor=x_actor, action='create_incident', target_table='incidents', target_id=row['id'], meta=payload)
        conn.commit()
    return dict(row)

@router.get('/{incident_id}', response_model=dict)
def get_incident(incident_id: UUID):
    with get_conn() as conn:
        row = conn.execute("select id, order_id, reporter_id, severity, status, text, resolution, created_at, updated_at from incidents where id=%s", (incident_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='incident not found')
    return dict(row)
