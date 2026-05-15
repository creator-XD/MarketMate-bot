"""
Общие обработчики: start, help, навигация и переключение языка.
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from database.models import User
from keyboards import (
    get_main_menu_keyboard,
    get_back_keyboard,
    get_cancel_keyboard,
    get_skip_keyboard,
    get_categories_keyboard,
    get_confirm_keyboard,
    get_rating_keyboard,
    get_review_comment_keyboard,
)
from config import BOT_NAME, SUPPORT_USERNAME, WELCOME_IMAGE_PATH
from utils.helpers import (
    safe_delete_message,
    safe_edit_or_answer,
    format_price,
)
from i18n import t
from states.states import (
    ListingStates, SearchStates, MessageStates, ProfileStates, ReviewStates,
)

logger = logging.getLogger(__name__)
router = Router(name="common")
PHOTOS_STATUS_MESSAGE_ID = "photos_status_message_id"


# ── Helpers ────────────────────────────────────────────────────────────────

async def _show_main_menu(target, lang: str):
    """Отправляет или повторно отправляет главное меню для Message и CallbackQuery."""
    welcome_text = t("welcome", lang, bot_name=BOT_NAME)
    welcome_image = FSInputFile(WELCOME_IMAGE_PATH)

    if isinstance(target, CallbackQuery):
        await safe_delete_message(target.message.bot, target.message.chat.id, target.message.message_id)
        await target.message.answer_photo(
            photo=welcome_image,
            caption=welcome_text,
            reply_markup=get_main_menu_keyboard(lang),
            parse_mode="HTML",
        )
    else:
        await target.answer_photo(
            photo=welcome_image,
            caption=welcome_text,
            reply_markup=get_main_menu_keyboard(lang),
            parse_mode="HTML",
        )


async def _resend_current_state_prompt(message: Message, state: FSMContext, lang: str):
    """
    Re-send the prompt for the current FSM state in the new language.
    Called after a language switch so the user sees the step in their new language.
    """
    from keyboards.keyboards import get_done_keyboard
    from config import MAX_PHOTOS
    from i18n import get_category_name as _get_cat_name

    current_state = await state.get_state()
    data = await state.get_data()

    if current_state is None:
        await _show_main_menu(message, lang)
        return

    # ── Создание объявления ──────────────────────────────────────────────────
    if current_state == ListingStates.waiting_for_title:
        await message.answer(
            t("listing_title_step", lang),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )

    elif current_state == ListingStates.waiting_for_description:
        await message.answer(
            t("listing_description_step", lang),
            reply_markup=get_skip_keyboard("skip_description", lang),
            parse_mode="HTML",
        )

    elif current_state == ListingStates.waiting_for_price:
        await message.answer(
            t("listing_price_step", lang),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )

    elif current_state == ListingStates.waiting_for_category:
        await message.answer(
            t("listing_category_step", lang),
            reply_markup=get_categories_keyboard(
                callback_prefix="new_listing_category",
                include_all=False,
                include_back=False,
                lang=lang,
            ),
            parse_mode="HTML",
        )

    elif current_state == ListingStates.waiting_for_photos:
        await message.answer(
            t("listing_photos_step", lang, max_photos=MAX_PHOTOS),
            reply_markup=get_skip_keyboard("skip_photos", lang),
            parse_mode="HTML",
        )

    elif current_state == ListingStates.confirm_listing:
        category_name = _get_cat_name(data.get("category", ""), lang)
        photos_count = len(data.get("photos", []))
        text = (
            t("listing_confirm_header", lang)
            + t("listing_confirm_title", lang, title=data.get("title", ""))
            + t("listing_confirm_price", lang, price=format_price(data.get("price", 0)))
            + t("listing_confirm_category", lang, category_name=category_name)
            + t("listing_confirm_photos", lang, count=photos_count)
        )
        if data.get("description"):
            desc_preview = data["description"][:100]
            if len(data["description"]) > 100:
                desc_preview += "..."
            text += t("listing_confirm_description", lang, desc=desc_preview)
        text += t("listing_confirm_question", lang)
        await message.answer(
            text,
            reply_markup=get_confirm_keyboard("confirm_create_listing", "cancel", lang),
            parse_mode="HTML",
        )

    # ── Редактирование объявления ───────────────────────────────────────────────────
    elif current_state == ListingStates.editing_title:
        listing_id = data.get("editing_listing_id")
        await message.answer(
            t("edit_title_prompt", lang, current="..."),
            reply_markup=get_back_keyboard(f"edit_listing:{listing_id}", lang),
            parse_mode="HTML",
        )

    elif current_state == ListingStates.editing_description:
        listing_id = data.get("editing_listing_id")
        await message.answer(
            t("edit_description_prompt", lang, current="..."),
            reply_markup=get_back_keyboard(f"edit_listing:{listing_id}", lang),
            parse_mode="HTML",
        )

    elif current_state == ListingStates.editing_price:
        listing_id = data.get("editing_listing_id")
        await message.answer(
            t("edit_price_prompt", lang, current=format_price(0)),
            reply_markup=get_back_keyboard(f"edit_listing:{listing_id}", lang),
            parse_mode="HTML",
        )

    elif current_state == ListingStates.editing_category:
        await message.answer(
            t("edit_category_prompt", lang, current="..."),
            reply_markup=get_categories_keyboard(
                callback_prefix="edit_category",
                include_all=False,
                include_back=False,
                lang=lang,
            ),
            parse_mode="HTML",
        )

    # ── Search ────────────────────────────────────────────────────────────
    elif current_state == SearchStates.waiting_for_query:
        await message.answer(
            t("search_keywords_prompt", lang),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )

    elif current_state == SearchStates.waiting_for_seller:
        await message.answer(
            t("search_seller_prompt", lang),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )

    elif current_state == SearchStates.waiting_for_location:
        await message.answer(
            t("search_location_prompt", lang),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )

    elif current_state == SearchStates.waiting_for_min_price:
        await message.answer(
            t("search_price_custom_min", lang),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )

    elif current_state == SearchStates.waiting_for_max_price:
        await message.answer(
            t("search_price_custom_max", lang),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )

    # ── Редактирование профиля ───────────────────────────────────────────────────
    elif current_state == ProfileStates.editing_location:
        await message.answer(
            t("edit_location_prompt", lang, current="..."),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )

    elif current_state == ProfileStates.editing_bio:
        await message.answer(
            t("edit_bio_prompt", lang, current="..."),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )

    # ── Messages ──────────────────────────────────────────────────────────
    elif current_state == MessageStates.waiting_for_message:
        await message.answer(
            t("contact_seller_header", lang, title="...", seller="..."),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )

    elif current_state == MessageStates.waiting_for_reply:
        await message.answer(
            t("reply_to_buyer_prompt", lang),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )

    # ── Reviews ───────────────────────────────────────────────────────────
    elif current_state == ReviewStates.waiting_for_rating:
        listing_id = data.get("listing_id", 0)
        await message.answer(
            t("review_prompt", lang, seller="...", title="..."),
            reply_markup=get_rating_keyboard(listing_id, lang),
            parse_mode="HTML",
        )

    elif current_state == ReviewStates.waiting_for_comment:
        rating = data.get("rating", 0)
        stars = "⭐" * rating
        await message.answer(
            t("rate_comment_prompt", lang, stars=stars, rating=rating),
            reply_markup=get_review_comment_keyboard(lang),
            parse_mode="HTML",
        )

    else:
        # Неизвестное состояние — возвращаемся в меню
        await _show_main_menu(message, lang)


# ── /start ─────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает команду /start."""
    await state.clear()

    user = await User.get_or_create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    logger.info(f"User started bot: {user.telegram_id} ({user.display_name})")
    await _show_main_menu(message, lang)


# ── /help ──────────────────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: Message, lang: str = "ru"):
    """Обрабатывает команду /help."""
    await message.answer(
        t("help", lang, support=SUPPORT_USERNAME),
        reply_markup=get_back_keyboard(lang=lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery, lang: str = "ru"):
    """Обрабатывает callback кнопки помощи."""
    await safe_edit_or_answer(
        callback,
        t("help", lang, support=SUPPORT_USERNAME),
        reply_markup=get_back_keyboard(lang=lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ── /cancel ────────────────────────────────────────────────────────────────

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает команду /cancel."""
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(t("nothing_to_cancel", lang), parse_mode="HTML")
        return

    data = await state.get_data()
    photos_status_message_id = data.get(PHOTOS_STATUS_MESSAGE_ID)
    if photos_status_message_id:
        await safe_delete_message(message.bot, message.chat.id, photos_status_message_id)

    await state.clear()
    await message.answer(
        t("operation_cancelled", lang),
        reply_markup=get_main_menu_keyboard(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Обрабатывает callback кнопки отмены."""
    data = await state.get_data()
    photos_status_message_id = data.get(PHOTOS_STATUS_MESSAGE_ID)
    if photos_status_message_id and photos_status_message_id != callback.message.message_id:
        await safe_delete_message(callback.message.bot, callback.message.chat.id, photos_status_message_id)

    await state.clear()
    await safe_delete_message(callback.message.bot, callback.message.chat.id, callback.message.message_id)
    welcome_image = FSInputFile(WELCOME_IMAGE_PATH)
    await callback.message.answer_photo(
        photo=welcome_image,
        caption=t("welcome", lang, bot_name=BOT_NAME),
        reply_markup=get_main_menu_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer(t("operation_cancelled", lang))


@router.callback_query(F.data == "back_to_menu")
async def callback_back_to_menu(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Обрабатывает callback возврата в меню."""
    await state.clear()
    await safe_delete_message(callback.message.bot, callback.message.chat.id, callback.message.message_id)
    welcome_image = FSInputFile(WELCOME_IMAGE_PATH)
    await callback.message.answer_photo(
        photo=welcome_image,
        caption=t("welcome", lang, bot_name=BOT_NAME),
        reply_markup=get_main_menu_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def callback_noop(callback: CallbackQuery):
    """Обрабатывает callback без действия, например индикаторы страниц."""
    await callback.answer()


# ── Переключение языка ──────────────────────────────────────────────────────

@router.message(Command("english"))
async def cmd_english(message: Message, state: FSMContext, lang: str = "ru"):
    """Переключает язык бота на английский."""
    if lang == "en":
        await message.answer(t("language_already_en", "en"))
        return

    user = await User.get_by_telegram_id(message.from_user.id)
    if user:
        await user.update(language="en")

    await message.answer(t("language_set_en", "en"))
    # Повторно отправляем подсказку текущего состояния на английском
    await _resend_current_state_prompt(message, state, "en")


@router.message(Command("russian"))
async def cmd_russian(message: Message, state: FSMContext, lang: str = "ru"):
    """Переключает язык бота на русский."""
    if lang == "ru":
        await message.answer(t("language_already_ru", "ru"))
        return

    user = await User.get_by_telegram_id(message.from_user.id)
    if user:
        await user.update(language="ru")

    await message.answer(t("language_set_ru", "ru"))
    # Повторно отправляем подсказку текущего состояния на русском
    await _resend_current_state_prompt(message, state, "ru")
