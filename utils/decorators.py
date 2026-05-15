"""
Decorator utilities for admin authentication and authorization.
"""
from functools import wraps
from aiogram import types
from config import ADMIN_TELEGRAM_IDS, ADMIN_ROLES
from database.admin_models import AdminUser
import logging

logger = logging.getLogger(__name__)


def require_admin(handler):
    """
    Декоратор для обязательной аутентификации администратора.
    Проверяет, есть ли Telegram ID пользователя в белом списке администраторов.
    """
    @wraps(handler)
    async def wrapper(event: types.Message | types.CallbackQuery, *args, **kwargs):
        # Получаем пользователя из события
        user = event.from_user

        # Проверяем, есть ли пользователь в белом списке администраторов
        if user.id not in ADMIN_TELEGRAM_IDS:
            logger.warning(f"Unauthorized admin access attempt by user {user.id}")
            if isinstance(event, types.Message):
                await event.answer("⛔ У вас нет доступа к админ-панели.")
            else:
                await event.answer("⛔ У вас нет доступа к админ-панели.", show_alert=True)
            return

        # Проверяем активную админскую роль в базе данных
        admin = await AdminUser.get_by_telegram_id(user.id)
        if not admin or not admin.is_active:
            logger.warning(f"Admin user {user.id} is not active in database")
            if isinstance(event, types.Message):
                await event.answer("⛔ Ваш админ-аккаунт не активен.")
            else:
                await event.answer("⛔ Ваш админ-аккаунт не активен.", show_alert=True)
            return

        # Удаляем admin из kwargs, если он добавлен middleware
        # чтобы избежать ошибки дублирования аргумента
        kwargs.pop('admin', None)

        # Передаём объект администратора в обработчик
        return await handler(event, admin, *args, **kwargs)

    return wrapper


def require_permission(permission: str):
    """
    Декоратор для проверки конкретного админского права.
    Должен использоваться вместе с @require_admin.
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(event: types.Message | types.CallbackQuery, admin: AdminUser, *args, **kwargs):
            # Проверяем наличие нужного права у администратора
            if not admin.has_permission(permission):
                logger.warning(
                    f"Admin {admin.user_id} attempted to access {permission} without permission"
                )
                if isinstance(event, types.Message):
                    await event.answer(f"⛔ У вас нет разрешения: {permission}")
                else:
                    await event.answer(f"⛔ У вас нет разрешения: {permission}", show_alert=True)
                return

            return await handler(event, admin, *args, **kwargs)

        return wrapper
    return decorator


async def is_admin(user_id: int) -> bool:
    """
    Проверяет, является ли пользователь администратором.
    Возвращает True, если пользователь есть в белом списке и имеет активную роль администратора.
    """
    if user_id not in ADMIN_TELEGRAM_IDS:
        return False

    admin = await AdminUser.get_by_telegram_id(user_id)
    return admin is not None and admin.is_active


async def get_admin_user(telegram_id: int) -> AdminUser | None:
    """
    Get admin user by Telegram ID.
    Returns None if user is not an admin or not active.
    """
    if telegram_id not in ADMIN_TELEGRAM_IDS:
        return None

    admin = await AdminUser.get_by_telegram_id(telegram_id)
    if admin and admin.is_active:
        return admin

    return None
