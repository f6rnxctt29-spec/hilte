from fastapi import APIRouter, HTTPException, Header
from uuid import UUID
from ..db import get_conn
from ..schemas import OrderCreate, OrderOut, OrderUpdate
from ..audit import log_action
from ..jsonutil import j

from datetime import datetime, timedelta, timezone

router = APIRouter(prefix='/orders', tags=['orders'])

@router.get('/upcoming', response_model=list[dict])
def upcoming_orders(hours: int = 24, limit: int = 200):
    now = datetime.now(timezone.utc)
    horizon = now + timedelta(hours=max(1, min(hours, 168)))
    with get_conn() as conn:
        rows = conn.execute(
            """
            select id, booking_id, scheduled_at, type, price, cost, margin, status, created_at
            from orders
            where scheduled_at is not null and scheduled_at >= %s and scheduled_at <= %s
            order by scheduled_at asc
            limit %s
            """,
            (now, horizon, limit),
        ).fetchall()
    # placeholder for future SLA model
    out = []
    for r in rows:
        d = dict(r)
        d['sla_risk'] = 'green'
        out.append(d)
    return out

@router.get('', response_model=list[OrderOut])
def list_orders(limit: int = 50):
    with get_conn() as conn:
        rows = conn.execute(
            """
            select id, booking_id, scheduled_at, type, items, price, cost, margin, status, created_at
            from orders
            order by created_at desc
            limit %s
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]

@router.post('', response_model=OrderOut)
def create_order(payload: OrderCreate, x_actor: str = Header(default='system')):
    with get_conn() as conn:
        row = conn.execute(
            """
            insert into orders (booking_id, scheduled_at, type, items, price, cost, status)
            values (%s,%s,%s,%s,%s,%s,%s)
            returning id, booking_id, scheduled_at, type, items, price, cost, margin, status, created_at
            """,
            (
                payload.booking_id,
                payload.scheduled_at,
                payload.type,
                j(payload.items),
                payload.price,
                payload.cost,
                payload.status,
            ),
        ).fetchone()
        log_action(conn, actor=x_actor, action='create_order', target_table='orders', target_id=row['id'], meta=payload.model_dump())
        conn.commit()
    return dict(row)

@router.get('/{order_id}', response_model=OrderOut)
def get_order(order_id: UUID):
    with get_conn() as conn:
        row = conn.execute(
            """
            select id, booking_id, scheduled_at, type, items, price, cost, margin, status, created_at
            from orders
            where id=%s
            """,
            (order_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='order not found')
    return dict(row)

@router.put('/{order_id}', response_model=OrderOut)
def update_order(order_id: UUID, payload: OrderUpdate, x_actor: str = Header(default='system')):
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail='empty update')

    sets = []
    args = []
    for k, v in data.items():
        sets.append(f"{k}=%s")
        if k == 'items' and v is not None:
            args.append(j(v))
        else:
            args.append(v)
    args.append(order_id)

    with get_conn() as conn:
        row = conn.execute(
            f"""
            update orders set {', '.join(sets)}
            where id=%s
            returning id, booking_id, scheduled_at, type, items, price, cost, margin, status, created_at
            """,
            tuple(args),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='order not found')
        log_action(conn, actor=x_actor, action='update_order', target_table='orders', target_id=order_id, meta=data)
        conn.commit()

    return dict(row)
