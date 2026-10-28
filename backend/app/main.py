from backend.app.api.v1.clustering import router as clustering_router
from fastapi import FastAPI
from backend.app.api.v1.forecast import router as forecast_router

from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.readings import router as readings_router
from backend.app.api.v1.devices import router as devices_router
from backend.app.api.v1.consumption import router as consumption_router
from backend.app.api.v1.bills import router as bills_router

from backend.app.api.v1.analytics import router as analytics_router
def create_app() -> FastAPI:
    app = FastAPI(
        title="UrjaSense API",
        description="AI-Based Energy Consumption Analytics Platform",
        version="0.1.0",
    )

    app.include_router(
        health_router,
        prefix="/api/v1",
        tags=["Health"],
    )

    app.include_router(
        readings_router,
        prefix="/api/v1/readings",
        tags=["Readings"],
    )

    app.include_router(
        devices_router,
        prefix="/api/v1/devices",
        tags=["Devices"],
    )

    app.include_router(
        consumption_router,
        prefix="/api/v1/consumption",
        tags=["Consumption Analytics"],
    )

    app.include_router(
        bills_router,
        prefix="/api/v1/bills",
        tags=["Billing"],
    )
    app.include_router(
        analytics_router,
        prefix="/api/v1/analytics",
        tags=["Anomaly Detection"],
    )
    app.include_router(
        clustering_router,
        prefix="/api/v1/clustering",
        tags=["Usage Pattern Clustering"],
    )
    app.include_router(
        forecast_router,
        prefix="/api/v1/forecast",
        tags=["Energy Forecasting"],
    )
    return app


app = create_app()
