from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from ..db import get_conn

router = APIRouter(prefix='/dash', tags=['dash'])

@router.get('/manager')
def manager_dash():
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    day_after = today_start + timedelta(days=2)

    with get_conn() as conn:
        today_row = conn.execute(
            "select count(*) as c from orders where scheduled_at >= %s and scheduled_at < %s",
            (today_start, tomorrow_start),
        ).fetchone()
        tomorrow_row = conn.execute(
            "select count(*) as c from orders where scheduled_at >= %s and scheduled_at < %s",
            (tomorrow_start, day_after),
        ).fetchone()

        today = int(today_row['c'] if today_row else 0)
        tomorrow = int(tomorrow_row['c'] if tomorrow_row else 0)

    return {
        'orders_today': int(today),
        'orders_tomorrow': int(tomorrow),
        'vip_week': [],
        'time_risks': [],
        'unpaid': 0,
        'quality_incidents': 0,
        'triggers_fired_today': [],
    }
