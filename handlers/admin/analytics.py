"""
Обработчики аналитики админ-панели.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models import User, Listing, Transaction
from keyboards.admin_keyboards import get_admin_analytics_keyboard, get_back_to_admin_keyboard
from utils.decorators import require_admin
from utils.helpers import safe_edit_or_answer
from database.admin_models import AdminUser
import logging

logger = logging.getLogger(__name__)

router = Router(name="admin_analytics")


@router.callback_query(F.data == "admin_analytics")
@require_admin
async def admin_analytics_menu(callback: CallbackQuery, admin: AdminUser):
    """Показывает меню аналитики администратора."""
    await safe_edit_or_answer(callback,
        "📈 <b>Аналитика</b>\n\n"
        "Выберите раздел:",
        reply_markup=get_admin_analytics_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_analytics:"))
@require_admin
async def admin_analytics_section(callback: CallbackQuery, admin: AdminUser):
    """Показывает аналитику выбранного раздела."""
    section = callback.data.split(":")[-1]

    if section == "users":
        stats = await User.get_statistics()
        text = "👥 <b>Статистика пользователей</b>\n\n"
        text += f"Всего пользователей: {stats.get('total', 0)}\n"
        text += f"Активных: {stats.get('active', 0)}\n"
        text += f"Заблокированных: {stats.get('blocked', 0)}\n"
    elif section == "listings":
        stats = await Listing.get_statistics()
        text = "📝 <b>Статистика объявлений</b>\n\n"
        text += f"Всего объявлений: {stats.get('total', 0)}\n"
        text += f"Активных: {stats.get('active', 0)}\n"
        text += f"Проданных: {stats.get('sold', 0)}\n"
    elif section == "transactions":
        stats = await Transaction.get_statistics()
        text = "💳 <b>Статистика транзакций</b>\n\n"
        text += f"Всего транзакций: {stats.get('total', 0)}\n"
        text += f"Завершенных: {stats.get('completed', 0)}\n"
        text += f"Ожидающих: {stats.get('pending', 0)}\n"
    else:
        await callback.answer("Неизвестный раздел", show_alert=True)
        return

    await safe_edit_or_answer(callback,
        text,
        reply_markup=get_back_to_admin_keyboard()
    )
    await callback.answer()
