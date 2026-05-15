"""
Обработчики управления транзакциями в админ-панели.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models import Transaction
from keyboards.admin_keyboards import get_admin_transactions_keyboard, get_back_to_admin_keyboard
from utils.decorators import require_admin
from utils.helpers import safe_edit_or_answer
from database.admin_models import AdminUser
import logging

logger = logging.getLogger(__name__)

router = Router(name="admin_transactions")


@router.callback_query(F.data == "admin_transactions")
@require_admin
async def admin_transactions_menu(callback: CallbackQuery, admin: AdminUser):
    """Показывает меню управления транзакциями."""
    await safe_edit_or_answer(callback,
        "💳 <b>Управление транзакциями</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_transactions_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_transactions:"))
@require_admin
async def admin_transactions_filter(callback: CallbackQuery, admin: AdminUser):
    """Обрабатывает фильтрацию транзакций."""
    filter_type = callback.data.split(":")[-1]

    # Получаем транзакции по фильтру через доступные методы
    if filter_type == "all":
        transactions = await Transaction.get_all(limit=100)
        title = "Все транзакции"
    elif filter_type == "pending":
        transactions = await Transaction.get_all(status="pending", limit=100)
        title = "Ожидающие транзакции"
    elif filter_type == "completed":
        transactions = await Transaction.get_all(status="completed", limit=100)
        title = "Завершенные транзакции"
    elif filter_type == "cancelled":
        transactions = await Transaction.get_all(status="cancelled", limit=100)
        title = "Отмененные транзакции"
    else:
        await callback.answer("Неизвестный фильтр", show_alert=True)
        return

    if not transactions:
        await safe_edit_or_answer(callback,
            f"💳 <b>{title}</b>\n\n"
            "Транзакции не найдены.",
            reply_markup=get_back_to_admin_keyboard()
        )
        await callback.answer()
        return

    text = f"💳 <b>{title}</b> ({len(transactions)})\n\n"
    for transaction in transactions[:10]:  # Показываем первые 10
        text += f"• Транзакция #{transaction.id}\n"

    if len(transactions) > 10:
        text += f"\n<i>... и еще {len(transactions) - 10}</i>"

    await safe_edit_or_answer(callback,
        text,
        reply_markup=get_back_to_admin_keyboard()
    )
    await callback.answer()
