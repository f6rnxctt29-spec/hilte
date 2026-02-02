from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import clients, bookings, orders, dash, ui, incidents, audit_logs, status

app = FastAPI(title='HILTE CRM+ERP API', version='0.1.0')

# Allow local dashboards (including file:// origin in some browsers) to call the API.
# Tight scope: localhost only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1", "http://localhost", "http://127.0.0.1:9000", "http://localhost:9000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router)
app.include_router(bookings.router)
app.include_router(orders.router)
app.include_router(dash.router)
app.include_router(ui.router)
app.include_router(incidents.router)
app.include_router(audit_logs.router)
app.include_router(status.router)

@app.get('/health')
def health():
    return {'status': 'ok'}
