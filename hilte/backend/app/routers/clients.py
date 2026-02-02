from fastapi import APIRouter, HTTPException, Header
from uuid import UUID
from ..db import get_conn
from ..schemas import ClientCreate, ClientOut, ClientUpdate
from psycopg.types.json import Json
from ..audit import log_action
from ..jsonutil import j

router = APIRouter(prefix='/clients', tags=['clients'])

@router.get('', response_model=list[ClientOut])
def list_clients(limit: int = 50):
    with get_conn() as conn:
        rows = conn.execute(
            """
            select id, name, status, phone, telegram, address, contact, preferences, created_at
            from clients
            order by created_at desc
            limit %s
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]

@router.post('', response_model=ClientOut)
def create_client(payload: ClientCreate, x_actor: str = Header(default='system')):
    with get_conn() as conn:
        row = conn.execute(
            """
            insert into clients (name, status, phone, telegram, address, contact, preferences)
            values (%s,%s,%s,%s,%s,%s,%s)
            returning id, name, status, phone, telegram, address, contact, preferences, created_at
            """,
            (
                payload.name,
                payload.status,
                payload.phone,
                payload.telegram,
                payload.address,
                j(payload.contact),
                j(payload.preferences),
            ),
        ).fetchone()
        log_action(conn, actor=x_actor, action='create_client', target_table='clients', target_id=row['id'], meta=payload.model_dump())
        conn.commit()
    return dict(row)

@router.get('/{client_id}', response_model=ClientOut)
def get_client(client_id: UUID):
    with get_conn() as conn:
        row = conn.execute(
            """
            select id, name, status, phone, telegram, address, contact, preferences, created_at
            from clients
            where id=%s
            """,
            (client_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='client not found')
    return dict(row)

@router.put('/{client_id}', response_model=ClientOut)
def update_client(client_id: UUID, payload: ClientUpdate, x_actor: str = Header(default='system')):
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail='empty update')

    sets = []
    args = []
    for k, v in data.items():
        sets.append(f"{k}=%s")
        if k in ('contact','preferences') and v is not None:
            args.append(j(v))
        else:
            args.append(Json(v) if k in ('contact','preferences') and v is not None else v)
    args.append(client_id)

    with get_conn() as conn:
        row = conn.execute(
            f"""
            update clients set {', '.join(sets)}
            where id=%s
            returning id, name, status, phone, telegram, address, contact, preferences, created_at
            """,
            tuple(args),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='client not found')
        log_action(conn, actor=x_actor, action='update_client', target_table='clients', target_id=client_id, meta=data)
        conn.commit()

    return dict(row)
