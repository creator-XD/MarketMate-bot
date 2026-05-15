"""
Admin authentication middleware.
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from config import ADMIN_TELEGRAM_IDS
from database.admin_models import AdminUser
import logging

logger = logging.getLogger(__name__)


class AdminAuthMiddleware(BaseMiddleware):
    """
    Middleware для аутентификации администраторов.
    Добавляет объект администратора в данные обработчика, если пользователь является администратором.
    """

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Проверяет, является ли пользователь администратором, и добавляет объект администратора в данные обработчика.
        Добавляет admin/is_admin в data только для реального администратора.
        """
        user = event.from_user

        # Проверяем, есть ли пользователь в белом списке администраторов
        if user.id in ADMIN_TELEGRAM_IDS:
            # Получаем администратора из базы данных
            admin = await AdminUser.get_by_telegram_id(user.id)
            if admin and admin.is_active:
                # Добавляем данные только для активного администратора
                data["admin"] = admin
                data["is_admin"] = True

        # Вызываем обработчик
        return await handler(event, data)
