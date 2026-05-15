"""
Главный роутер и дашборд админ-панели.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from database.models import User, Listing, Transaction
from database.admin_models import AdminUser, AdminAuditLog
from keyboards.admin_keyboards import get_admin_main_menu_keyboard
from keyboards import get_main_menu_keyboard
from utils.decorators import require_admin
from utils.helpers import safe_delete_message, safe_edit_or_answer, safe_send_or_edit_state_message
from utils.admin_helpers import format_admin_dashboard
from config import BOT_NAME, WELCOME_IMAGE_PATH
from i18n import t
import logging

logger = logging.getLogger(__name__)

admin_router = Router(name="admin")
ADMIN_MENU_MESSAGE_ID = "admin_menu_message_id"

# Импортируем и подключаем подроутеры
from . import user_management, listing_management, transaction_management, analytics, audit, review_management

admin_router.include_router(user_management.router)
admin_router.include_router(listing_management.router)
admin_router.include_router(transaction_management.router)
admin_router.include_router(analytics.router)
admin_router.include_router(audit.router)
admin_router.include_router(review_management.router)


@admin_router.message(Command("admin"))
@require_admin
async def admin_command(message: Message, admin: AdminUser, state: FSMContext):
    """Обрабатывает команду /admin и показывает админ-панель."""
    await safe_send_or_edit_state_message(
        message,
        state,
        ADMIN_MENU_MESSAGE_ID,
        "🔧 <b>Админ-панель</b>\n\nВыберите раздел:",
        reply_markup=get_admin_main_menu_keyboard(),
        parse_mode="HTML",
    )


@admin_router.callback_query(F.data == "admin_menu")
@require_admin
async def admin_menu_callback(callback: CallbackQuery, admin: AdminUser):
    """Показывает главное меню администратора."""
    await safe_edit_or_answer(callback,
        "🔧 <b>Админ-панель</b>\n\nВыберите раздел:",
        reply_markup=get_admin_main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin_dashboard")
@require_admin
async def admin_dashboard_callback(callback: CallbackQuery, admin: AdminUser):
    """Показывает дашборд администратора со статистикой."""
    # Получаем статистику
    user_stats = await User.get_statistics()
    listing_stats = await Listing.get_statistics()
    transaction_stats = await Transaction.get_statistics()

    stats = {
        "user_stats": user_stats,
        "listing_stats": listing_stats,
        "transaction_stats": transaction_stats,
    }

    dashboard_text = format_admin_dashboard(stats)

    await safe_edit_or_answer(callback,
        dashboard_text,
        reply_markup=get_admin_main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@admin_router.callback_query(F.data == "main_menu")
@require_admin
async def main_menu_callback(callback: CallbackQuery, admin: AdminUser, lang: str = "ru"):
    """Возвращает из админ-панели в основное меню пользователя."""
    welcome_text = t("welcome", lang, bot_name=BOT_NAME)

    await safe_delete_message(callback.message.bot, callback.message.chat.id, callback.message.message_id)
    welcome_image = FSInputFile(WELCOME_IMAGE_PATH)
    await callback.message.answer_photo(
        photo=welcome_image,
        caption=welcome_text,
        reply_markup=get_main_menu_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()
