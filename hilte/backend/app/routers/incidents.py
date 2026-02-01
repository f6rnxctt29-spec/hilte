from fastapi import APIRouter, HTTPException
from uuid import UUID
from ..db import get_conn
from ..schemas import BookingOut
import json

router = APIRouter(prefix='/incidents', tags=['incidents'])

@router.get('', response_model=list)
def list_incidents(limit: int = 50):
    with get_conn() as conn:
        rows = conn.execute(
            "select id, order_id, reporter_id, severity, status, text, resolution, created_at, updated_at from incidents order by created_at desc limit %s",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]

@router.post('', response_model=dict)
def create_incident(payload: dict):
    with get_conn() as conn:
        row = conn.execute(
            "insert into incidents (order_id, reporter_id, severity, status, text, resolution) values (%s,%s,%s,%s,%s,%s) returning id, order_id, reporter_id, severity, status, text, resolution, created_at, updated_at",
            (
                payload.get('order_id'),
                payload.get('reporter_id'),
                payload.get('severity'),
                payload.get('status','open'),
                payload.get('text'),
                payload.get('resolution')
            ),
        ).fetchone()
        # write audit log
        conn.execute(
            "insert into audit_logs (actor, action, target_table, target_id, meta) values (%s,%s,%s,%s,%s)",
            ('system','create_incident','incidents', row[0], json.dumps({}))
        )
        conn.commit()
    return dict(row)

@router.get('/{incident_id}', response_model=dict)
def get_incident(incident_id: UUID):
    with get_conn() as conn:
        row = conn.execute("select id, order_id, reporter_id, severity, status, text, resolution, created_at, updated_at from incidents where id=%s", (incident_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='incident not found')
    return dict(row)
