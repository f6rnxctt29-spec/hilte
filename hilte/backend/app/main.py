from fastapi import FastAPI

from .routers import clients, bookings, orders, dash, ui, incidents

app = FastAPI(title='HILTE CRM+ERP API', version='0.1.0')

app.include_router(clients.router)
app.include_router(bookings.router)
app.include_router(orders.router)
app.include_router(dash.router)
app.include_router(ui.router)
app.include_router(incidents.router)

@app.get('/health')
def health():
    return {'status': 'ok'}
