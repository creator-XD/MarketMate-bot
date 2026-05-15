"""
Language middleware — injects `lang` into every handler's data dict.
"""
from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from database.models import User


class LanguageMiddleware(BaseMiddleware):
    """Загружает язык пользователя из БД и добавляет `lang` в данные обработчика."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        lang = "ru"  # значение по умолчанию

        # Определяем Telegram-пользователя из события
        tg_user = None
        if isinstance(event, Message):
            tg_user = event.from_user
        elif isinstance(event, CallbackQuery):
            tg_user = event.from_user

        if tg_user:
            try:
                db_user = await User.get_by_telegram_id(tg_user.id)
                if db_user and db_user.language:
                    lang = db_user.language
            except Exception:
                pass  # при ошибке БД оставляем значение по умолчанию

        data["lang"] = lang
        return await handler(event, data)
