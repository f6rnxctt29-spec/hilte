from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from ..db import get_conn

router = APIRouter(prefix='/dash', tags=['dash'])

@router.get('/control_center')
def control_center():
    """Read-only control center (decision-first).

    Returns ops + risks + finance snapshot for the dashboard UI.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    day_after = today_start + timedelta(days=2)
    horizon = now + timedelta(hours=8)

    with get_conn() as conn:
        # ops counts
        today_row = conn.execute(
            "select count(*) as c from orders where scheduled_at >= %s and scheduled_at < %s",
            (today_start, tomorrow_start),
        ).fetchone()
        tomorrow_row = conn.execute(
            "select count(*) as c from orders where scheduled_at >= %s and scheduled_at < %s",
            (tomorrow_start, day_after),
        ).fetchone()

        # finance (based on scheduled today)
        fin_row = conn.execute(
            """
            select
              coalesce(sum(price),0) as revenue,
              coalesce(sum(margin),0) as margin,
              count(*) as orders_count,
              coalesce(avg(case when price>0 then (margin/price) else null end),0) as avg_margin
            from orders
            where scheduled_at >= %s and scheduled_at < %s
            """,
            (today_start, tomorrow_start),
        ).fetchone()

        below_row = conn.execute(
            """
            select count(*) as c
            from orders
            where scheduled_at >= %s and scheduled_at < %s
              and price > 0
              and (margin/price) < 0.30
            """,
            (today_start, tomorrow_start),
        ).fetchone()

        # risks
        inc_row = conn.execute(
            "select count(*) as c from incidents where status='open'",
        ).fetchone()
        repeat_row = conn.execute(
            "select count(*) as c from incidents where status='open' and resolution='repeat_visit'",
        ).fetchone()

        # upcoming
        upcoming = conn.execute(
            """
            select id, scheduled_at, status, margin
            from orders
            where scheduled_at >= %s and scheduled_at <= %s
            order by scheduled_at asc
            limit 20
            """,
            (now, horizon),
        ).fetchall()

        # triggers today (from trigger_logs)
        trig = conn.execute(
            """
            select id, name, status, result, ran_at
            from trigger_logs
            where ran_at >= %s
            order by ran_at desc
            limit 20
            """,
            (today_start,),
        ).fetchall()

        # overdue payments stub (until invoicing/payment logic is in)
        overdue_payments = 0

    orders_today = int(today_row['c'] if today_row else 0)
    orders_tomorrow = int(tomorrow_row['c'] if tomorrow_row else 0)

    revenue = float(fin_row['revenue']) if fin_row else 0.0
    margin = float(fin_row['margin']) if fin_row else 0.0
    orders_count = int(fin_row['orders_count']) if fin_row else 0
    avg_margin_pct = int(round((float(fin_row['avg_margin']) if fin_row else 0.0) * 100))
    below = int(below_row['c'] if below_row else 0)

    open_incidents = int(inc_row['c'] if inc_row else 0)
    repeat_visits = int(repeat_row['c'] if repeat_row else 0)

    # SLA risk placeholder: share of upcoming orders as a proxy (will become real with logistics/SLA)
    sla_risk = min(1.0, max(0.0, (orders_today / 10.0)))

    return {
        'ops': {
            'orders_today': orders_today,
            'orders_tomorrow': orders_tomorrow,
            'sla_risk': sla_risk,
            'upcoming_orders': [dict(r) for r in upcoming],
        },
        'risks': {
            'open_incidents': open_incidents,
            'repeat_visits': repeat_visits,
            'triggers_today': [dict(r) for r in trig],
        },
        'finance': {
            'revenue_today': revenue,
            'margin_today': margin,
            'orders_count': orders_count,
            'avg_margin_pct': avg_margin_pct,
            'below_margin_floor': below,
            'overdue_payments': overdue_payments,
        },
    }

@router.get('/series')
def series(days: int = 7):
    days = max(2, min(int(days), 30))
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=days-1)).replace(hour=0, minute=0, second=0, microsecond=0)

    with get_conn() as conn:
        rows = conn.execute(
            """
            select date_trunc('day', scheduled_at) as day,
                   count(*) as orders,
                   coalesce(sum(price),0) as revenue,
                   coalesce(sum(margin),0) as margin
            from orders
            where scheduled_at is not null and scheduled_at >= %s
            group by 1
            order by 1 asc
            """,
            (start,),
        ).fetchall()

    by_day = {r['day'].date().isoformat(): dict(r) for r in rows}
    out = []
    for i in range(days):
        d = (start + timedelta(days=i)).date().isoformat()
        r = by_day.get(d)
        if not r:
            out.append({"day": d, "orders": 0, "revenue": 0, "margin": 0})
        else:
            out.append({
                "day": d,
                "orders": int(r['orders']),
                "revenue": float(r['revenue']),
                "margin": float(r['margin']),
            })
    return out

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
