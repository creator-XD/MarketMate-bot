"""
Audit logging middleware for admin actions.
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.admin_models import AdminAuditLog, AdminUser
import logging

logger = logging.getLogger(__name__)


class AuditLoggerMiddleware(BaseMiddleware):
    """
    Middleware для автоматического логирования действий администратора.
    Логирует действия после выполнения обработчика, если audit_action есть в данных состояния.
    """

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Выполняет обработчик и логирует действие аудита, если оно задано.
        """
        # Сначала вызываем обработчик
        result = await handler(event, data)

        # Проверяем, нужно ли логировать админское действие
        if "admin" in data and data["admin"] is not None:
            admin: AdminUser = data["admin"]

            # Проверяем наличие audit_action в данных состояния
            state = data.get("state")
            if state:
                state_data = await state.get_data()
                audit_action = state_data.get("audit_action")

                if audit_action:
                    try:
                        # Создаём запись журнала аудита
                        await AdminAuditLog.create(
                            admin_id=admin.user_id,
                            action=audit_action.get("action", "unknown"),
                            target_type=audit_action.get("target_type"),
                            target_id=audit_action.get("target_id"),
                            details=audit_action.get("details", {})
                        )

                        logger.info(
                            f"Admin action logged: {audit_action.get('action')} "
                            f"by admin {admin.user_id}"
                        )

                        # Очищаем действие аудита из состояния
                        await state.update_data(audit_action=None)

                    except Exception as e:
                        logger.error(f"Failed to log admin action: {e}")

        return result
