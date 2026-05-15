"""
Handlers module for the Telegram Marketplace Bot.
"""
from aiogram import Router

from .common import router as common_router
from .listings import router as listings_router
from .search import router as search_router
from .messages import router as messages_router
from .reviews import router as reviews_router
from .profile import router as profile_router
from .reports import router as reports_router
from .admin import admin_router


def get_all_routers() -> list[Router]:
    """Возвращает все роутеры для регистрации."""
    return [
        admin_router,  # Админский роутер первым для приоритета
        listings_router,
        search_router,
        messages_router,
        reviews_router,
        reports_router,
        profile_router,
        common_router,
    ]


__all__ = [
    "get_all_routers",
    "admin_router",
    "common_router",
    "listings_router",
    "search_router",
    "messages_router",
    "reviews_router",
    "reports_router",
    "profile_router",
]
