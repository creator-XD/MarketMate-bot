"""
Обработчики управления объявлениями: создание, редактирование, удаление и просмотр.
"""
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from database.models import User, Listing, ListingPhoto, Favorite
from keyboards import (
    get_main_menu_keyboard,
    get_my_listings_keyboard,
    get_categories_keyboard,
    get_listing_detail_keyboard,
    get_edit_listing_keyboard,
    get_cancel_keyboard,
    get_skip_keyboard,
    get_confirm_keyboard,
    get_back_keyboard,
    get_condition_keyboard,
)
from keyboards.keyboards import get_done_keyboard, get_listings_keyboard
from states import ListingStates
from utils import format_listing_text, get_category_name
from utils.helpers import (
    validate_title,
    validate_description,
    validate_price,
    safe_edit_or_answer,
    safe_delete_message,
    safe_edit_message_text,
    safe_send_or_edit_state_message,
    format_search_results_header,
    format_price,
)
from config import MAX_PHOTOS, PAGE_SIZE
from i18n import t

logger = logging.getLogger(__name__)
router = Router(name="listings")
PHOTOS_STATUS_MESSAGE_ID = "photos_status_message_id"
PROMPT_MESSAGE_ID = "prompt_message_id"


# ==================== Меню моих объявлений ====================

@router.message(F.text == "/mylistings")
async def cmd_my_listings(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает команду /mylistings."""
    await state.clear()
    await message.answer(
        t("my_listings_menu", lang),
        reply_markup=get_my_listings_keyboard(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "my_listings")
async def callback_my_listings(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Обрабатывает callback меню моих объявлений."""
    await state.clear()
    await safe_edit_or_answer(
        callback,
        t("my_listings_menu", lang),
        reply_markup=get_my_listings_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "my_active")
async def callback_my_active_listings(callback: CallbackQuery, lang: str = "ru"):
    """Показывает активные объявления пользователя."""
    user = await User.get_by_telegram_id(callback.from_user.id)
    listings = await Listing.get_by_user(user.id, status="active")

    if not listings:
        await safe_edit_or_answer(
            callback,
            t("no_active_listings", lang),
            reply_markup=get_my_listings_keyboard(lang),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    text = t("active_listings_header", lang, count=len(listings))

    keyboard = get_listings_keyboard(listings, callback_prefix="view_own_listing")
    keyboard.inline_keyboard.append([
        {"text": t("btn_back", lang), "callback_data": "my_listings"}
    ])

    await safe_edit_or_answer(callback, text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "my_sold")
async def callback_my_sold_listings(callback: CallbackQuery, lang: str = "ru"):
    """Показывает проданные объявления пользователя."""
    user = await User.get_by_telegram_id(callback.from_user.id)
    listings = await Listing.get_by_user(user.id, status="sold")

    if not listings:
        await safe_edit_or_answer(
            callback,
            t("no_sold_listings", lang),
            reply_markup=get_my_listings_keyboard(lang),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    text = t("sold_listings_header", lang, count=len(listings))

    keyboard = get_listings_keyboard(listings, callback_prefix="view_own_listing")
    keyboard.inline_keyboard.append([
        {"text": t("btn_back", lang), "callback_data": "my_listings"}
    ])

    await safe_edit_or_answer(callback, text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


# ==================== Создание объявления ====================

@router.callback_query(F.data == "add_listing")
async def callback_add_listing(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Запускает процесс создания объявления."""
    user = await User.get_by_telegram_id(callback.from_user.id)
    if not user.is_active:
        reason_text = t("suspension_reason_prefix", lang, reason=user.suspension_reason) if user.suspension_reason else ""
        until_text = (
            t("suspension_until_prefix", lang, until=user.suspended_until.strftime("%d.%m.%Y %H:%M"))
            if user.suspended_until else ""
        )
        await safe_edit_or_answer(
            callback,
            t("access_restricted", lang, reason=reason_text, until=until_text),
            reply_markup=get_main_menu_keyboard(lang),
            parse_mode="HTML",
        )
        await callback.answer(t("account_blocked_toast", lang), show_alert=True)
        return

    await state.set_state(ListingStates.waiting_for_title)

    prompt_message = await safe_edit_or_answer(
        callback,
        t("listing_title_step", lang),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML",
    )
    await state.update_data(
        photos=[],
        **{PROMPT_MESSAGE_ID: (prompt_message.message_id if prompt_message else callback.message.message_id)},
    )
    await callback.answer()


@router.message(ListingStates.waiting_for_title)
async def process_listing_title(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает название объявления."""
    is_valid, error = validate_title(message.text, lang)

    if not is_valid:
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            t("error_invalid_title", lang, error=error),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )
        return

    await state.update_data(title=message.text.strip())
    await state.set_state(ListingStates.waiting_for_description)

    await safe_send_or_edit_state_message(
        message,
        state,
        PROMPT_MESSAGE_ID,
        t("listing_description_step", lang),
        reply_markup=get_skip_keyboard(skip_callback="skip_description", lang=lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "skip_description", ListingStates.waiting_for_description)
async def skip_description(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Пропускает шаг описания."""
    await state.update_data(description="")
    await state.set_state(ListingStates.waiting_for_price)

    prompt_message = await safe_edit_or_answer(
        callback,
        t("listing_price_step", lang),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML",
    )
    await state.update_data(**{PROMPT_MESSAGE_ID: (prompt_message.message_id if prompt_message else callback.message.message_id)})
    await callback.answer()


@router.message(ListingStates.waiting_for_description)
async def process_listing_description(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает описание объявления."""
    is_valid, error = validate_description(message.text, lang)

    if not is_valid:
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            t("error_description_too_long", lang, error=error),
            reply_markup=get_skip_keyboard(skip_callback="skip_description", lang=lang),
            parse_mode="HTML",
        )
        return

    await state.update_data(description=message.text.strip())
    await state.set_state(ListingStates.waiting_for_price)

    await safe_send_or_edit_state_message(
        message,
        state,
        PROMPT_MESSAGE_ID,
        t("listing_price_step", lang),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(ListingStates.waiting_for_price)
async def process_listing_price(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает цену объявления."""
    is_valid, price, error = validate_price(message.text, lang)

    if not is_valid:
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            t("error_invalid_price", lang, error=error),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )
        return

    await state.update_data(price=price)
    await state.set_state(ListingStates.waiting_for_category)

    await safe_send_or_edit_state_message(
        message,
        state,
        PROMPT_MESSAGE_ID,
        t("listing_category_step", lang),
        reply_markup=get_categories_keyboard(
            callback_prefix="new_listing_category",
            include_all=False,
            include_back=False,
            lang=lang,
        ),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("new_listing_category:"), ListingStates.waiting_for_category)
async def process_listing_category(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Обрабатывает выбор категории объявления."""
    category = callback.data.split(":")[1]
    await state.update_data(category=category)
    await state.set_state(ListingStates.waiting_for_condition)

    prompt_message = await safe_edit_or_answer(
        callback,
        t("listing_condition_step", lang),
        reply_markup=get_condition_keyboard(callback_prefix="new_listing_condition", lang=lang),
        parse_mode="HTML",
    )
    await state.update_data(**{PROMPT_MESSAGE_ID: (prompt_message.message_id if prompt_message else callback.message.message_id)})
    await callback.answer()


@router.callback_query(F.data.startswith("new_listing_condition:"), ListingStates.waiting_for_condition)
async def process_listing_condition(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Обрабатывает выбор состояния товара."""
    condition = callback.data.split(":")[1]
    await state.update_data(condition=condition)
    await state.set_state(ListingStates.waiting_for_photos)

    prompt_message = await safe_edit_or_answer(
        callback,
        t("listing_photos_step", lang, max_photos=MAX_PHOTOS),
        reply_markup=get_skip_keyboard(skip_callback="skip_photos", lang=lang),
        parse_mode="HTML",
    )
    await state.update_data(**{PROMPT_MESSAGE_ID: (prompt_message.message_id if prompt_message else callback.message.message_id)})
    await callback.answer()


@router.callback_query(F.data == "skip_photos", ListingStates.waiting_for_photos)
async def skip_photos(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Пропускает шаг фотографий."""
    await show_listing_confirmation(callback, state, lang)


async def _send_or_update_photos_status(message: Message, state: FSMContext, text: str, lang: str):
    """Поддерживает одно статусное сообщение с inline-клавиатурой при загрузке фото."""
    data = await state.get_data()
    status_message_id = data.get(PHOTOS_STATUS_MESSAGE_ID)
    reply_markup = get_done_keyboard(done_callback="photos_done", lang=lang)

    if status_message_id:
        edited = await safe_edit_message_text(
            message.bot,
            message.chat.id,
            status_message_id,
            text,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
        if edited:
            return

        await safe_delete_message(message.bot, message.chat.id, status_message_id)

    sent_message = await message.answer(
        text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )
    await state.update_data(**{PHOTOS_STATUS_MESSAGE_ID: sent_message.message_id})


@router.message(ListingStates.waiting_for_photos, F.photo)
async def process_listing_photo(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает фотографию объявления."""
    data = await state.get_data()
    photos = data.get("photos", [])

    if len(photos) >= MAX_PHOTOS:
        await _send_or_update_photos_status(
            message,
            state,
            t("photos_max_reached", lang, max_photos=MAX_PHOTOS),
            lang,
        )
        return

    photo = message.photo[-1]
    photos.append({
        "file_id": photo.file_id,
        "file_unique_id": photo.file_unique_id,
    })

    await state.update_data(photos=photos)

    remaining = MAX_PHOTOS - len(photos)
    text = t("photo_added", lang, current=len(photos), max=MAX_PHOTOS)
    if remaining > 0:
        text += t("photos_remaining", lang, remaining=remaining)

    await _send_or_update_photos_status(message, state, text, lang)


@router.callback_query(F.data == "photos_done", ListingStates.waiting_for_photos)
async def photos_done(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Завершает добавление фотографий."""
    await show_listing_confirmation(callback, state, lang)


async def show_listing_confirmation(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Показывает подтверждение объявления."""
    data = await state.get_data()
    photos_status_message_id = data.pop(PHOTOS_STATUS_MESSAGE_ID, None)
    if photos_status_message_id and photos_status_message_id != callback.message.message_id:
        await safe_delete_message(callback.message.bot, callback.message.chat.id, photos_status_message_id)

    await state.set_data(data)

    category_name = get_category_name(data["category"], lang)
    condition_key = f"condition_{data.get('condition', 'new')}"
    condition_name = t(condition_key, lang)
    photos_count = len(data.get("photos", []))

    text = (
        t("listing_confirm_header", lang)
        + t("listing_confirm_title", lang, title=data["title"])
        + t("listing_confirm_price", lang, price=format_price(data["price"]))
        + t("listing_confirm_category", lang, category_name=category_name)
        + t("listing_confirm_condition", lang, condition=condition_name)
        + t("listing_confirm_photos", lang, count=photos_count)
    )

    if data.get("description"):
        desc_preview = data["description"][:100]
        if len(data["description"]) > 100:
            desc_preview += "..."
        text += t("listing_confirm_description", lang, desc=desc_preview)

    text += t("listing_confirm_question", lang)

    await state.set_state(ListingStates.confirm_listing)

    prompt_message = await safe_edit_or_answer(
        callback,
        text,
        reply_markup=get_confirm_keyboard("confirm_create_listing", "cancel", lang),
        parse_mode="HTML",
    )
    await state.update_data(**{PROMPT_MESSAGE_ID: (prompt_message.message_id if prompt_message else callback.message.message_id)})
    await callback.answer()


@router.callback_query(F.data == "confirm_create_listing", ListingStates.confirm_listing)
async def confirm_create_listing(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Создаёт объявление."""
    data = await state.get_data()
    user = await User.get_by_telegram_id(callback.from_user.id)

    listing = await Listing.create(
        user_id=user.id,
        title=data["title"],
        description=data.get("description", ""),
        price=data["price"],
        category=data["category"],
        condition=data.get("condition", "new"),
    )

    photos = data.get("photos", [])
    for i, photo in enumerate(photos):
        await ListingPhoto.create(
            listing_id=listing.id,
            file_id=photo["file_id"],
            file_unique_id=photo["file_unique_id"],
            is_primary=(i == 0),
        )

    await state.clear()

    logger.info(f"Listing created: {listing.id} by user {user.telegram_id}")

    await safe_edit_or_answer(
        callback,
        t("listing_published_text", lang, title=listing.title),
        reply_markup=get_main_menu_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer(t("listing_created", lang))


# ==================== Просмотр объявления ====================

@router.callback_query(F.data.startswith("view_listing:"))
async def view_listing(callback: CallbackQuery, bot: Bot, lang: str = "ru"):
    """Показывает объявление покупателю."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id, with_photos=True, with_user=True)

    if not listing:
        await callback.answer(t("listing_not_found", lang), show_alert=True)
        return

    await listing.increment_views()

    user = await User.get_by_telegram_id(callback.from_user.id)
    is_owner = listing.user_id == user.id
    is_favorite = await Favorite.is_favorite(user.id, listing_id)

    text = format_listing_text(listing, user=listing.user, detailed=True, lang=lang)

    if listing.photos:
        await safe_delete_message(callback.message.bot, callback.message.chat.id, callback.message.message_id)

        if len(listing.photos) == 1:
            await bot.send_photo(
                callback.from_user.id,
                listing.photos[0].file_id,
                caption=text,
                reply_markup=get_listing_detail_keyboard(listing_id, is_owner, is_favorite, seller_id=listing.user_id, lang=lang),
                parse_mode="HTML",
            )
        else:
            media = [
                InputMediaPhoto(
                    media=photo.file_id,
                    caption=text if i == 0 else None,
                    parse_mode="HTML" if i == 0 else None,
                )
                for i, photo in enumerate(listing.photos)
            ]
            await bot.send_media_group(callback.from_user.id, media)
            await bot.send_message(
                callback.from_user.id,
                t("select_action", lang),
                reply_markup=get_listing_detail_keyboard(listing_id, is_owner, is_favorite, seller_id=listing.user_id, lang=lang),
            )
    else:
        await safe_edit_or_answer(
            callback,
            text,
            reply_markup=get_listing_detail_keyboard(listing_id, is_owner, is_favorite, seller_id=listing.user_id, lang=lang),
            parse_mode="HTML",
        )

    await callback.answer()


@router.callback_query(F.data.startswith("view_own_listing:"))
async def view_own_listing(callback: CallbackQuery, bot: Bot, lang: str = "ru"):
    """Показывает своё объявление продавцу."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id, with_photos=True)

    if not listing:
        await callback.answer(t("listing_not_found", lang), show_alert=True)
        return

    text = format_listing_text(listing, detailed=True, lang=lang)

    if listing.photos:
        await safe_delete_message(callback.message.bot, callback.message.chat.id, callback.message.message_id)

        if len(listing.photos) == 1:
            await bot.send_photo(
                callback.from_user.id,
                listing.photos[0].file_id,
                caption=text,
                reply_markup=get_listing_detail_keyboard(listing_id, is_owner=True, seller_id=listing.user_id, lang=lang),
                parse_mode="HTML",
            )
        else:
            media = [
                InputMediaPhoto(
                    media=photo.file_id,
                    caption=text if i == 0 else None,
                    parse_mode="HTML" if i == 0 else None,
                )
                for i, photo in enumerate(listing.photos)
            ]
            await bot.send_media_group(callback.from_user.id, media)
            await bot.send_message(
                callback.from_user.id,
                t("select_action", lang),
                reply_markup=get_listing_detail_keyboard(listing_id, is_owner=True, seller_id=listing.user_id, lang=lang),
            )
    else:
        await safe_edit_or_answer(
            callback,
            text,
            reply_markup=get_listing_detail_keyboard(listing_id, is_owner=True, seller_id=listing.user_id, lang=lang),
            parse_mode="HTML",
        )

    await callback.answer()


@router.callback_query(F.data == "back_to_listings")
async def back_to_listings(callback: CallbackQuery, state: FSMContext, bot: Bot, lang: str = "ru"):
    """Возвращает пользователя на страницу результатов поиска или просмотра."""
    from keyboards.keyboards import get_pagination_keyboard

    data = await state.get_data()

    query = data.get("search_query")
    category = data.get("search_category")
    min_price = data.get("search_min_price")
    max_price = data.get("search_max_price")
    seller_id = data.get("search_seller_id")
    seller_name = data.get("search_seller_name")
    location = data.get("search_location")
    page = data.get("search_page", 1)

    offset = (page - 1) * PAGE_SIZE

    listings = await Listing.search(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        seller_id=seller_id,
        location=location,
        limit=PAGE_SIZE,
        offset=offset,
    )
    total = await Listing.count_search(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        seller_id=seller_id,
        location=location,
    )

    if not listings:
        await safe_edit_or_answer(
            callback,
            t("no_listings", lang),
            reply_markup=get_main_menu_keyboard(lang),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE if total > 0 else 1

    text = format_search_results_header(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        seller_name=seller_name,
        location=location,
        total=total,
        lang=lang,
    )
    text += t("search_select_listing", lang)

    keyboard = get_listings_keyboard(listings)

    if total_pages > 1:
        extra_data = f"{query or ''}|{category or ''}|{min_price or ''}|{max_price or ''}|{seller_id or ''}|{seller_name or ''}|{location or ''}"
        pagination = get_pagination_keyboard(page, total_pages, "search", extra_data, lang)
        keyboard.inline_keyboard.extend(pagination.inline_keyboard)
    else:
        keyboard.inline_keyboard.append([
            {"text": t("btn_menu", lang), "callback_data": "back_to_menu"},
            {"text": t("btn_new_search", lang), "callback_data": "search"},
        ])

    await safe_edit_or_answer(
        callback,
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Редактирование объявления ====================

@router.callback_query(F.data.startswith("edit_listing:"))
async def edit_listing_menu(callback: CallbackQuery, lang: str = "ru"):
    """Показывает меню редактирования объявления."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id)

    if not listing:
        await callback.answer(t("listing_not_found", lang), show_alert=True)
        return

    user = await User.get_by_telegram_id(callback.from_user.id)
    if listing.user_id != user.id:
        await callback.answer(t("cannot_edit_others", lang), show_alert=True)
        return

    await safe_edit_or_answer(
        callback,
        t("edit_listing_menu", lang, title=listing.title),
        reply_markup=get_edit_listing_keyboard(listing_id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_field:"))
async def edit_field(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Начинает редактирование выбранного поля."""
    parts = callback.data.split(":")
    field = parts[1]
    listing_id = int(parts[2])

    listing = await Listing.get_by_id(listing_id)
    if not listing:
        await callback.answer(t("listing_not_found", lang), show_alert=True)
        return

    await state.update_data(editing_listing_id=listing_id)

    if field == "title":
        await state.set_state(ListingStates.editing_title)
        prompt_message = await safe_edit_or_answer(
            callback,
            t("edit_title_prompt", lang, current=listing.title),
            reply_markup=get_back_keyboard(f"edit_listing:{listing_id}", lang),
            parse_mode="HTML",
        )
    elif field == "description":
        await state.set_state(ListingStates.editing_description)
        current_desc = (
            listing.description[:100] + "..."
            if listing.description and len(listing.description) > 100
            else (listing.description or t("no_description", lang))
        )
        prompt_message = await safe_edit_or_answer(
            callback,
            t("edit_description_prompt", lang, current=current_desc),
            reply_markup=get_back_keyboard(f"edit_listing:{listing_id}", lang),
            parse_mode="HTML",
        )
    elif field == "price":
        await state.set_state(ListingStates.editing_price)
        prompt_message = await safe_edit_or_answer(
            callback,
            t("edit_price_prompt", lang, current=format_price(listing.price)),
            reply_markup=get_back_keyboard(f"edit_listing:{listing_id}", lang),
            parse_mode="HTML",
        )
    elif field == "category":
        await state.set_state(ListingStates.editing_category)
        prompt_message = await safe_edit_or_answer(
            callback,
            t("edit_category_prompt", lang, current=get_category_name(listing.category, lang)),
            reply_markup=get_categories_keyboard(
                callback_prefix="edit_category",
                include_all=False,
                include_back=False,
                lang=lang,
            ),
            parse_mode="HTML",
        )
    elif field == "condition":
        await state.set_state(ListingStates.editing_condition)
        current_condition = t(f"condition_{listing.condition}", lang)
        prompt_message = await safe_edit_or_answer(
            callback,
            t("edit_condition_prompt", lang, current=current_condition),
            reply_markup=get_condition_keyboard(callback_prefix="edit_condition", lang=lang),
            parse_mode="HTML",
        )
    elif field == "photos":
        prompt_message = await safe_edit_or_answer(
            callback,
            t("edit_photos_info", lang),
            reply_markup=get_back_keyboard(f"edit_listing:{listing_id}", lang),
            parse_mode="HTML",
        )

    if "prompt_message" in locals():
        await state.update_data(**{PROMPT_MESSAGE_ID: (prompt_message.message_id if prompt_message else callback.message.message_id)})

    await callback.answer()


@router.message(ListingStates.editing_title)
async def process_edit_title(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает изменённое название."""
    is_valid, error = validate_title(message.text, lang)
    if not is_valid:
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            t("error_invalid_title", lang, error=error),
        )
        return

    data = await state.get_data()
    listing_id = data["editing_listing_id"]
    prompt_message_id = data.get(PROMPT_MESSAGE_ID)
    listing = await Listing.get_by_id(listing_id)

    await listing.update(title=message.text.strip())
    await state.clear()

    edited = await safe_edit_message_text(
        message.bot,
        message.chat.id,
        prompt_message_id,
        t("listing_updated", lang),
        reply_markup=get_edit_listing_keyboard(listing_id, lang),
        parse_mode="HTML",
    )
    if not edited:
        await message.answer(
            t("listing_updated", lang),
            reply_markup=get_edit_listing_keyboard(listing_id, lang),
            parse_mode="HTML",
        )


@router.message(ListingStates.editing_description)
async def process_edit_description(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает изменённое описание."""
    is_valid, error = validate_description(message.text, lang)
    if not is_valid:
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            f"❌ {error}",
        )
        return

    data = await state.get_data()
    listing_id = data["editing_listing_id"]
    prompt_message_id = data.get(PROMPT_MESSAGE_ID)
    listing = await Listing.get_by_id(listing_id)

    await listing.update(description=message.text.strip())
    await state.clear()

    edited = await safe_edit_message_text(
        message.bot,
        message.chat.id,
        prompt_message_id,
        t("listing_updated", lang),
        reply_markup=get_edit_listing_keyboard(listing_id, lang),
        parse_mode="HTML",
    )
    if not edited:
        await message.answer(
            t("listing_updated", lang),
            reply_markup=get_edit_listing_keyboard(listing_id, lang),
            parse_mode="HTML",
        )


@router.message(ListingStates.editing_price)
async def process_edit_price(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает изменённую цену."""
    is_valid, price, error = validate_price(message.text, lang)
    if not is_valid:
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            t("error_invalid_price", lang, error=error),
        )
        return

    data = await state.get_data()
    listing_id = data["editing_listing_id"]
    prompt_message_id = data.get(PROMPT_MESSAGE_ID)
    listing = await Listing.get_by_id(listing_id)

    await listing.update(price=price)
    await state.clear()

    edited = await safe_edit_message_text(
        message.bot,
        message.chat.id,
        prompt_message_id,
        t("listing_updated", lang),
        reply_markup=get_edit_listing_keyboard(listing_id, lang),
        parse_mode="HTML",
    )
    if not edited:
        await message.answer(
            t("listing_updated", lang),
            reply_markup=get_edit_listing_keyboard(listing_id, lang),
            parse_mode="HTML",
        )


@router.callback_query(F.data.startswith("edit_category:"), ListingStates.editing_category)
async def process_edit_category(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Обрабатывает изменённую категорию."""
    category = callback.data.split(":")[1]
    data = await state.get_data()
    listing_id = data["editing_listing_id"]
    listing = await Listing.get_by_id(listing_id)

    await listing.update(category=category)
    await state.clear()

    await safe_edit_or_answer(
        callback,
        t("listing_updated", lang),
        reply_markup=get_edit_listing_keyboard(listing_id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_condition:"), ListingStates.editing_condition)
async def process_edit_condition(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Обрабатывает изменённое состояние товара."""
    condition = callback.data.split(":")[1]
    data = await state.get_data()
    listing_id = data["editing_listing_id"]
    listing = await Listing.get_by_id(listing_id)

    await listing.update(condition=condition)
    await state.clear()

    await safe_edit_or_answer(
        callback,
        t("listing_updated", lang),
        reply_markup=get_edit_listing_keyboard(listing_id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Удаление объявления ====================

@router.callback_query(F.data.startswith("delete_listing:"))
async def delete_listing_confirm(callback: CallbackQuery, lang: str = "ru"):
    """Запрашивает подтверждение удаления объявления."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id)

    if not listing:
        await callback.answer(t("listing_not_found", lang), show_alert=True)
        return

    user = await User.get_by_telegram_id(callback.from_user.id)
    if listing.user_id != user.id:
        await callback.answer(t("cannot_delete_others", lang), show_alert=True)
        return

    await safe_edit_or_answer(
        callback,
        t("delete_confirm", lang, title=listing.title),
        reply_markup=get_confirm_keyboard(
            confirm_callback=f"confirm_delete:{listing_id}",
            cancel_callback=f"view_own_listing:{listing_id}",
            lang=lang,
        ),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete_listing(callback: CallbackQuery, lang: str = "ru"):
    """Удаляет объявление."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id)

    if listing:
        await listing.delete()
        logger.info(f"Listing deleted: {listing_id}")

    await safe_edit_or_answer(
        callback,
        t("listing_deleted", lang),
        reply_markup=get_my_listings_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Отметка как проданное ====================

@router.callback_query(F.data.startswith("mark_sold:"))
async def mark_as_sold(callback: CallbackQuery, lang: str = "ru"):
    """Отмечает объявление как проданное."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id)

    if not listing:
        await callback.answer(t("listing_not_found", lang), show_alert=True)
        return

    user = await User.get_by_telegram_id(callback.from_user.id)
    if listing.user_id != user.id:
        await callback.answer(t("cannot_change_others", lang), show_alert=True)
        return

    await listing.update(status="sold")

    await safe_edit_or_answer(
        callback,
        t("mark_sold_success", lang, title=listing.title),
        reply_markup=get_my_listings_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer(t("mark_sold_toast", lang))


# ==================== Избранное ====================

@router.message(F.text == "/favorites")
async def cmd_favorites(message: Message, lang: str = "ru"):
    """Обрабатывает команду /favorites."""
    user = await User.get_by_telegram_id(message.from_user.id)
    listings = await Favorite.get_user_favorites(user.id)

    if not listings:
        await message.answer(
            t("favorites_empty", lang),
            reply_markup=get_main_menu_keyboard(lang),
            parse_mode="HTML",
        )
        return

    keyboard = get_listings_keyboard(listings)
    keyboard.inline_keyboard.append([
        {"text": t("btn_back_to_menu", lang), "callback_data": "back_to_menu"}
    ])

    await message.answer(
        t("favorites_header", lang, count=len(listings)),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "favorites")
async def callback_favorites(callback: CallbackQuery, lang: str = "ru"):
    """Показывает избранное."""
    user = await User.get_by_telegram_id(callback.from_user.id)
    listings = await Favorite.get_user_favorites(user.id)

    if not listings:
        await safe_edit_or_answer(
            callback,
            t("favorites_empty", lang),
            reply_markup=get_main_menu_keyboard(lang),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    keyboard = get_listings_keyboard(listings)
    keyboard.inline_keyboard.append([
        {"text": t("btn_back_to_menu", lang), "callback_data": "back_to_menu"}
    ])

    await safe_edit_or_answer(
        callback,
        t("favorites_header", lang, count=len(listings)),
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("add_favorite:"))
async def add_to_favorites(callback: CallbackQuery, lang: str = "ru"):
    """Добавляет объявление в избранное."""
    listing_id = int(callback.data.split(":")[1])
    user = await User.get_by_telegram_id(callback.from_user.id)

    await Favorite.add(user.id, listing_id)

    listing = await Listing.get_by_id(listing_id)
    is_owner = listing.user_id == user.id if listing else False
    seller_id = listing.user_id if listing else None

    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_listing_detail_keyboard(listing_id, is_owner, is_favorite=True, seller_id=seller_id, lang=lang)
        )
    except Exception:
        pass

    await callback.answer(t("added_to_favorites", lang))


@router.callback_query(F.data.startswith("remove_favorite:"))
async def remove_from_favorites(callback: CallbackQuery, lang: str = "ru"):
    """Удаляет объявление из избранного."""
    listing_id = int(callback.data.split(":")[1])
    user = await User.get_by_telegram_id(callback.from_user.id)

    await Favorite.remove(user.id, listing_id)

    listing = await Listing.get_by_id(listing_id)
    is_owner = listing.user_id == user.id if listing else False
    seller_id = listing.user_id if listing else None

    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_listing_detail_keyboard(listing_id, is_owner, is_favorite=False, seller_id=seller_id, lang=lang)
        )
    except Exception:
        pass

    await callback.answer(t("removed_from_favorites", lang))
