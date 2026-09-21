from .health import router as health_router
from .chat import router as chat_router
from .dashboard import router as dashboard_router
from .sales import router as sales_router
from .inventory import router as inventory_router
from .hr import router as hr_router
from .activity import router as activity_router
from .analytics import router as analytics_router

__all__ = [
    "health_router",
    "chat_router",
    "dashboard_router",
    "sales_router",
    "inventory_router",
    "hr_router",
    "activity_router",
    "analytics_router"
]
