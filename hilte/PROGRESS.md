# HILTE CRM+ERP — PROGRESS

## Done
- Project skeleton created: hilte/{backend,frontend,db,ops,docs}
- Core DB schema applied (clients, objects, staff, bookings, orders)
- Applied migration: hilte/db/03_mvp_schema.sql (incidents, audit_logs, triggers)
- Seeded test data: 10 clients, 20 bookings, 15 orders

## In progress
- Backend FastAPI: DB connection + CRUD endpoints (clients/bookings/orders)
- Manager dashboards (stubs → real queries)

## Latest changes
- clients: добавлены поля phone, telegram, address
- orders: зафиксирована status machine (pending→confirmed→in_progress→qa_hold→done→invoiced→paid)

## Blockers
- None

## Next
1) Add migrations for: payments/invoices, costs, trigger runner
2) Implement dashboards queries
3) Frontend wireframes (Manager/Coordinator/Quality/Finance)
