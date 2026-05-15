"""
Handlers for user-submitted reports on listings and other users.
"""
import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database.models import User, Listing, UserReport
from database.admin_models import AdminUser
from keyboards import get_main_menu_keyboard
from keyboards.keyboards import (
    get_report_listing_keyboard,
    get_report_user_keyboard,
    get_report_comment_keyboard,
)
from states import ReportStates
from utils.helpers import safe_edit_or_answer, escape_html
from i18n import t

logger = logging.getLogger(__name__)
router = Router(name="reports")

# Автоматически отмечаем объявление после такого числа жалоб
AUTO_FLAG_THRESHOLD = 3

LISTING_REASON_KEYS = {
    "spam": "report_reason_spam",
    "fraud": "report_reason_fraud",
    "inappropriate": "report_reason_inappropriate",
    "wrong_category": "report_reason_wrong_category",
    "other": "report_reason_other",
}
USER_REASON_KEYS = {
    "spam": "report_reason_spam",
    "scam": "report_reason_scam",
    "abuse": "report_reason_abuse",
    "other": "report_reason_other",
}


# ==================== Точки входа ====================

@router.callback_query(F.data.startswith("report_listing:"))
async def report_listing_start(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Показывает выбор причины жалобы на объявление."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id, with_user=True)

    if not listing:
        await callback.answer(t("listing_not_found", lang), show_alert=True)
        return

    user = await User.get_by_telegram_id(callback.from_user.id)

    if listing.user_id == user.id:
        await callback.answer(t("report_cannot_report_self", lang), show_alert=True)
        return

    if await UserReport.exists(user.id, "listing", listing_id):
        await callback.answer(t("report_already_sent", lang), show_alert=True)
        return

    seller_id = listing.user_id
    await safe_edit_or_answer(
        callback,
        t("report_listing_header", lang, title=escape_html(listing.title)),
        reply_markup=get_report_listing_keyboard(listing_id, seller_id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("report_user:"))
async def report_user_start(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Показывает выбор причины жалобы на пользователя."""
    user_id = int(callback.data.split(":")[1])
    target_user = await User.get_by_id(user_id)

    if not target_user:
        await callback.answer(t("seller_not_found", lang), show_alert=True)
        return

    reporter = await User.get_by_telegram_id(callback.from_user.id)

    if target_user.id == reporter.id:
        await callback.answer(t("report_cannot_report_self", lang), show_alert=True)
        return

    if await UserReport.exists(reporter.id, "user", user_id):
        await callback.answer(t("report_already_sent", lang), show_alert=True)
        return

    await safe_edit_or_answer(
        callback,
        t("report_user_header", lang, name=escape_html(target_user.display_name)),
        reply_markup=get_report_user_keyboard(user_id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Причина выбрана ====================

@router.callback_query(F.data.startswith("report_reason:"))
async def report_reason_selected(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Пользователь выбрал причину — запрашиваем необязательный комментарий."""
    parts = callback.data.split(":")
    # report_reason:<type>:<target_id>:<reason>
    target_type = parts[1]
    target_id = int(parts[2])
    reason = parts[3]

    await state.set_state(ReportStates.waiting_for_comment)
    await state.update_data(
        report_target_type=target_type,
        report_target_id=target_id,
        report_reason=reason,
    )

    await safe_edit_or_answer(
        callback,
        t("report_comment_prompt", lang),
        reply_markup=get_report_comment_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "skip_report_comment", ReportStates.waiting_for_comment)
async def skip_report_comment(callback: CallbackQuery, state: FSMContext, bot: Bot, lang: str = "ru"):
    """Сохраняет жалобу без комментария."""
    await _save_report(callback, state, bot, lang, comment=None)


@router.message(ReportStates.waiting_for_comment)
async def process_report_comment(message: Message, state: FSMContext, bot: Bot, lang: str = "ru"):
    """Сохраняет жалобу с комментарием пользователя."""
    comment = message.text.strip()[:500] if message.text else None
    await _save_report(message, state, bot, lang, comment=comment)


# ==================== Сохранение и уведомление ====================

async def _save_report(event, state: FSMContext, bot: Bot, lang: str, comment: str):
    """Сохраняет жалобу, автоматически отмечает цель при достижении порога и уведомляет администраторов."""
    data = await state.get_data()
    await state.clear()

    target_type = data.get("report_target_type")
    target_id = data.get("report_target_id")
    reason = data.get("report_reason")

    is_callback = isinstance(event, CallbackQuery)
    from_user = event.from_user

    reporter = await User.get_by_telegram_id(from_user.id)

    # Защита от дублей при гонке запросов
    if await UserReport.exists(reporter.id, target_type, target_id):
        if is_callback:
            await event.answer(t("report_already_sent", lang), show_alert=True)
        else:
            await event.answer(t("report_already_sent", lang))
        return

    try:
        await UserReport.create(
            reporter_id=reporter.id,
            target_type=target_type,
            target_id=target_id,
            reason=reason,
            comment=comment,
        )
    except Exception:
        # Сработало ограничение UNIQUE — жалоба уже есть
        if is_callback:
            await event.answer(t("report_already_sent", lang), show_alert=True)
        else:
            await event.answer(t("report_already_sent", lang))
        return

    count = await UserReport.count_by_target(target_type, target_id)
    auto_flagged = False

    if target_type == "listing" and count >= AUTO_FLAG_THRESHOLD:
        listing = await Listing.get_by_id(target_id)
        if listing and not listing.flagged:
            await listing.update(
                flagged=1,
                flag_reason=f"Auto-flagged after {count} user reports",
            )
            auto_flagged = True

    # Уведомляем администраторов
    await _notify_admins(bot, reporter, target_type, target_id, reason, comment, count, auto_flagged, lang)

    # Подтверждаем отправителю жалобы
    text = t("report_success", lang)
    if auto_flagged:
        text += t("report_auto_flagged", lang)

    if is_callback:
        await safe_edit_or_answer(event, text, reply_markup=get_main_menu_keyboard(lang), parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, reply_markup=get_main_menu_keyboard(lang), parse_mode="HTML")

    logger.info(f"Report saved: {target_type} #{target_id} by user {reporter.id}, reason={reason}")


async def _notify_admins(bot: Bot, reporter: User, target_type: str, target_id: int,
                         reason: str, comment: str, count: int, auto_flagged: bool, lang: str):
    """Отправляет уведомление всем активным администраторам."""
    admins = await AdminUser.get_all(active_only=True)
    if not admins:
        return

    comment_line = t("report_admin_comment_line", "ru", comment=escape_html(comment)) if comment else ""
    reporter_str = escape_html(reporter.display_name)
    if reporter.username:
        reporter_str += f" (@{reporter.username})"

    if target_type == "listing":
        listing = await Listing.get_by_id(target_id)
        if not listing:
            return
        reason_label = t(f"report_reason_{reason}", "ru")
        notify_text = t(
            "report_admin_notify_listing", "ru",
            listing_id=target_id,
            title=escape_html(listing.title),
            reporter=reporter_str,
            reason=reason_label,
            comment_line=comment_line,
            count=count,
        )
    else:
        target_user = await User.get_by_id(target_id)
        if not target_user:
            return
        reason_label = t(f"report_reason_{reason}", "ru")
        notify_text = t(
            "report_admin_notify_user", "ru",
            user_id=target_id,
            name=escape_html(target_user.display_name),
            reporter=reporter_str,
            reason=reason_label,
            comment_line=comment_line,
            count=count,
        )

    if auto_flagged:
        notify_text += t("report_auto_flagged", "ru")

    for admin in admins:
        if admin.user and admin.user.telegram_id:
            try:
                await bot.send_message(admin.user.telegram_id, notify_text, parse_mode="HTML")
            except Exception as e:
                logger.warning(f"Could not notify admin {admin.user.telegram_id}: {e}")
