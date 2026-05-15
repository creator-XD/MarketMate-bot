"""
Обработчики управления профилем пользователя.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models import User, Listing
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from keyboards import (
    get_main_menu_keyboard,
    get_back_keyboard,
    get_cancel_keyboard,
)
from keyboards.keyboards import remove_keyboard, get_listings_keyboard
from states import ProfileStates
from utils.helpers import format_user_profile, escape_html, safe_edit_or_answer
from i18n import t

logger = logging.getLogger(__name__)
router = Router(name="profile")


def get_profile_keyboard(user_id: int = None, lang: str = "ru"):
    """Возвращает клавиатуру управления профилем."""
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=t("btn_edit_location", lang), callback_data="edit_location"),
        InlineKeyboardButton(text=t("btn_edit_bio", lang), callback_data="edit_bio"),
    )
    if user_id is not None:
        builder.row(
            InlineKeyboardButton(text=t("btn_my_reviews", lang), callback_data=f"seller_reviews:{user_id}"),
        )
    builder.row(
        InlineKeyboardButton(text=t("btn_back_to_menu", lang), callback_data="back_to_menu"),
    )

    return builder.as_markup()


@router.message(F.text == "/profile")
async def cmd_profile(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает команду /profile."""
    await state.clear()
    user = await User.get_by_telegram_id(message.from_user.id)

    active_listings = await Listing.get_by_user(user.id, status="active")
    sold_listings = await Listing.get_by_user(user.id, status="sold")

    text = format_user_profile(user, lang)
    text += t("profile_stats", lang, active=len(active_listings), sold=len(sold_listings))

    await message.answer(
        text,
        reply_markup=get_profile_keyboard(user.id, lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "profile")
async def callback_profile(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Показывает профиль пользователя."""
    await state.clear()
    user = await User.get_by_telegram_id(callback.from_user.id)

    active_listings = await Listing.get_by_user(user.id, status="active")
    sold_listings = await Listing.get_by_user(user.id, status="sold")

    text = format_user_profile(user, lang)
    text += t("profile_stats", lang, active=len(active_listings), sold=len(sold_listings))

    await safe_edit_or_answer(
        callback,
        text,
        reply_markup=get_profile_keyboard(user.id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Редактирование местоположения ====================

@router.callback_query(F.data == "edit_location")
async def edit_location(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Начинает редактирование местоположения."""
    await state.set_state(ProfileStates.editing_location)

    user = await User.get_by_telegram_id(callback.from_user.id)
    current_location = user.location or t("not_specified", lang)

    await safe_edit_or_answer(
        callback,
        t("edit_location_prompt", lang, current=escape_html(current_location)),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(ProfileStates.editing_location)
async def process_location(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает обновление местоположения."""
    location = message.text.strip()

    if len(location) > 100:
        await message.answer(t("location_too_long", lang), reply_markup=get_cancel_keyboard(lang))
        return

    user = await User.get_by_telegram_id(message.from_user.id)
    await user.update(location=location)

    await state.clear()
    await message.answer(
        t("location_updated", lang, location=escape_html(location)),
        reply_markup=get_profile_keyboard(user.id, lang),
        parse_mode="HTML",
    )


# ==================== Редактирование описания профиля ====================

@router.callback_query(F.data == "edit_bio")
async def edit_bio(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Начинает редактирование описания профиля."""
    await state.set_state(ProfileStates.editing_bio)

    user = await User.get_by_telegram_id(callback.from_user.id)
    current_bio = user.bio or t("not_specified", lang)

    await safe_edit_or_answer(
        callback,
        t("edit_bio_prompt", lang, current=escape_html(current_bio)),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(ProfileStates.editing_bio)
async def process_bio(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает обновление описания профиля."""
    bio = message.text.strip()

    if len(bio) > 500:
        await message.answer(t("bio_too_long", lang), reply_markup=get_cancel_keyboard(lang))
        return

    user = await User.get_by_telegram_id(message.from_user.id)
    await user.update(bio=bio)

    await state.clear()
    await message.answer(
        t("bio_updated", lang, bio=escape_html(bio)),
        reply_markup=get_profile_keyboard(user.id, lang),
        parse_mode="HTML",
    )


# ==================== Объявления продавца (публичный вид) ====================

@router.callback_query(F.data.startswith("seller_listings:"))
async def view_seller_listings(callback: CallbackQuery, lang: str = "ru"):
    """Показывает все активные объявления продавца."""
    seller_id = int(callback.data.split(":")[1])

    seller = await User.get_by_id(seller_id)
    if not seller:
        await callback.answer(t("seller_not_found", lang), show_alert=True)
        return

    listings = await Listing.get_by_user(seller_id, status="active")

    if not listings:
        await safe_edit_or_answer(
            callback,
            t("seller_no_listings", lang, seller=seller.display_name),
            reply_markup=get_back_keyboard("back_to_menu", lang),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    keyboard = get_listings_keyboard(listings, callback_prefix="view_listing")
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text=t("btn_back_to_menu", lang), callback_data="back_to_menu")
    ])

    await safe_edit_or_answer(
        callback,
        t("seller_listings_header", lang, seller=seller.display_name, count=len(listings)),
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Будущее: настройки платежей ====================

@router.callback_query(F.data == "payment_settings")
async def payment_settings(callback: CallbackQuery, lang: str = "ru"):
    """Показывает настройки платежей (заглушка на будущее)."""
    await safe_edit_or_answer(
        callback,
        t("payment_settings", lang),
        reply_markup=get_back_keyboard("profile", lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Будущее: верификация ====================

@router.callback_query(F.data == "get_verified")
async def get_verified(callback: CallbackQuery, lang: str = "ru"):
    """Показывает варианты верификации (заглушка на будущее)."""
    await safe_edit_or_answer(
        callback,
        t("verification", lang),
        reply_markup=get_back_keyboard("profile", lang),
        parse_mode="HTML",
    )
    await callback.answer()
