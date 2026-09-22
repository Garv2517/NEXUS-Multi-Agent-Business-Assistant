from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .core.config import settings
from .db.connection import initialize_database
from .repositories.analytics_repository import AnalyticsDatabaseNotFoundError
from .api import (
    health_router,
    chat_router,
    dashboard_router,
    sales_router,
    inventory_router,
    hr_router,
    activity_router,
    analytics_router,
    risk_router,
    forecast_router
)

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus.backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes and seeds the database automatically on startup."""
    logger.info("Initializing Nexus SQLite database...")
    try:
        initialize_database()
        logger.info("Database initialized and ready.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}", exc_info=True)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.2.0",
    description="Backend foundation for Nexus — Multi-Agent Business Assistant (Phase B2: Real Tools + SQLite)",
    lifespan=lifespan
)

# Configure CORS
origins = [
    settings.FRONTEND_ORIGIN,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
unique_origins = list(dict.fromkeys(origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=unique_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(dashboard_router)
app.include_router(sales_router)
app.include_router(inventory_router)
app.include_router(hr_router)
app.include_router(activity_router)
app.include_router(analytics_router)
app.include_router(risk_router)
app.include_router(forecast_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs": "/docs",
        "mode": "sqlite_tools"
    }


# Exception handler for missing analytics database -> HTTP 503
@app.exception_handler(AnalyticsDatabaseNotFoundError)
async def analytics_database_not_found_handler(request: Request, exc: AnalyticsDatabaseNotFoundError):
    logger.warning(f"Analytics database unavailable on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Analytics dataset unavailable"}
    )


# Safe generic error handler for unexpected server errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."}
    )
