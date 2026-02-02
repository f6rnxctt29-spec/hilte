from fastapi import APIRouter, HTTPException, Header
from uuid import UUID
from ..db import get_conn
from ..schemas import BookingCreate, BookingOut, BookingUpdate, OrderCreate, OrderOut
from psycopg.types.json import Json
from ..audit import log_action
from ..jsonutil import j

router = APIRouter(prefix='/bookings', tags=['bookings'])

@router.get('', response_model=list[BookingOut])
def list_bookings(limit: int = 50):
    with get_conn() as conn:
        rows = conn.execute(
            """
            select id, client_id, object_id, payload, status, created_at
            from bookings
            order by created_at desc
            limit %s
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]

@router.post('', response_model=BookingOut)
def create_booking(payload: BookingCreate, x_actor: str = Header(default='system')):
    with get_conn() as conn:
        row = conn.execute(
            """
            insert into bookings (client_id, object_id, payload, status)
            values (%s,%s,%s,%s)
            returning id, client_id, object_id, payload, status, created_at
            """,
            (payload.client_id, payload.object_id, j(payload.payload), payload.status),
        ).fetchone()
        log_action(conn, actor=x_actor, action='create_booking', target_table='bookings', target_id=row['id'], meta=payload.model_dump())
        conn.commit()
    return dict(row)

@router.get('/{booking_id}', response_model=BookingOut)
def get_booking(booking_id: UUID):
    with get_conn() as conn:
        row = conn.execute(
            """
            select id, client_id, object_id, payload, status, created_at
            from bookings
            where id=%s
            """,
            (booking_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='booking not found')
    return dict(row)

@router.put('/{booking_id}', response_model=BookingOut)
def update_booking(booking_id: UUID, payload: BookingUpdate, x_actor: str = Header(default='system')):
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail='empty update')

    sets = []
    args = []
    for k, v in data.items():
        sets.append(f"{k}=%s")
        if k == 'payload' and v is not None:
            args.append(j(v))
        else:
            args.append(Json(v) if k == 'payload' and v is not None else v)
    args.append(booking_id)

    with get_conn() as conn:
        row = conn.execute(
            f"""
            update bookings set {', '.join(sets)}
            where id=%s
            returning id, client_id, object_id, payload, status, created_at
            """,
            tuple(args),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='booking not found')
        log_action(conn, actor=x_actor, action='update_booking', target_table='bookings', target_id=booking_id, meta=data)
        conn.commit()

    return dict(row)

@router.post('/{booking_id}/convert', response_model=OrderOut)
def convert_booking_to_order(booking_id: UUID, payload: OrderCreate, x_actor: str = Header(default='system')):
    with get_conn() as conn:
        booking = conn.execute('select id, status from bookings where id=%s', (booking_id,)).fetchone()
        if not booking:
            raise HTTPException(status_code=404, detail='booking not found')

        row = conn.execute(
            """
            insert into orders (booking_id, scheduled_at, type, items, price, cost, status)
            values (%s,%s,%s,%s,%s,%s,%s)
            returning id, booking_id, scheduled_at, type, items, price, cost, margin, status, created_at
            """,
            (
                booking_id,
                payload.scheduled_at,
                payload.type,
                j(payload.items),
                payload.price,
                payload.cost,
                payload.status,
            ),
        ).fetchone()

        conn.execute("update bookings set status=%s where id=%s", ('converted', booking_id))
        log_action(conn, actor=x_actor, action='convert_booking_to_order', target_table='bookings', target_id=booking_id, meta={'order_id': str(row['id'])})
        conn.commit()

    return dict(row)
