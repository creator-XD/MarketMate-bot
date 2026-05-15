"""
Handlers for search and filtering functionality.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models import User, Listing
from keyboards import (
    get_main_menu_keyboard,
    get_search_keyboard,
    get_categories_keyboard,
    get_cancel_keyboard,
)
from keyboards.keyboards import (
    get_listings_keyboard,
    get_price_range_keyboard,
    get_pagination_keyboard,
)
from states import SearchStates
from utils.helpers import (
    format_search_results_header,
    validate_price,
    safe_edit_or_answer,
    safe_send_or_edit_state_message,
    escape_html,
)
from config import PAGE_SIZE
from i18n import t

logger = logging.getLogger(__name__)
router = Router(name="search")
PROMPT_MESSAGE_ID = "prompt_message_id"


# ==================== Меню поиска ====================

@router.message(F.text == "/search")
async def cmd_search(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает команду /search."""
    await state.clear()
    await message.answer(
        t("search_menu", lang),
        reply_markup=get_search_keyboard(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "search")
async def callback_search(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Показывает варианты поиска."""
    await state.clear()
    await safe_edit_or_answer(
        callback,
        t("search_menu", lang),
        reply_markup=get_search_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Просмотр всех объявлений ====================

@router.callback_query(F.data == "browse")
async def browse_listings(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Показывает все объявления."""
    await state.clear()
    await state.update_data(
        search_query=None,
        search_category=None,
        search_min_price=None,
        search_max_price=None,
        search_page=1,
    )
    await show_search_results(callback, state, lang)


# ==================== Поиск по ключевым словам ====================

@router.callback_query(F.data == "search_keywords")
async def search_by_keywords(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Начинает поиск по ключевым словам."""
    await state.set_state(SearchStates.waiting_for_query)
    await state.update_data(
        search_category=None,
        search_min_price=None,
        search_max_price=None,
        search_page=1,
    )

    prompt_message = await safe_edit_or_answer(
        callback,
        t("search_keywords_prompt", lang),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML",
    )
    await state.update_data(**{PROMPT_MESSAGE_ID: (prompt_message.message_id if prompt_message else callback.message.message_id)})
    await callback.answer()


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает поисковый запрос."""
    query = message.text.strip()

    if len(query) < 2:
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            t("search_query_too_short", lang),
            reply_markup=get_cancel_keyboard(lang),
        )
        return

    await state.update_data(search_query=query, search_page=1)
    await state.set_state(SearchStates.browsing_results)

    await show_search_results_message(message, state, lang)


# ==================== Просмотр по категории ====================

@router.callback_query(F.data == "search_category")
async def search_by_category(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Показывает выбор категории для поиска."""
    await state.update_data(
        search_query=None,
        search_min_price=None,
        search_max_price=None,
        search_page=1,
    )

    await safe_edit_or_answer(
        callback,
        t("search_categories_header", lang),
        reply_markup=get_categories_keyboard(
            callback_prefix="browse_category",
            include_all=True,
            include_back=True,
            back_callback="search",
            lang=lang,
        ),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("browse_category:"))
async def process_category_browse(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Обрабатывает выбор категории."""
    category = callback.data.split(":")[1]

    if category == "all":
        await state.update_data(search_category=None)
    else:
        await state.update_data(search_category=category)

    await state.update_data(search_page=1)
    await state.set_state(SearchStates.browsing_results)

    await show_search_results(callback, state, lang)


# ==================== Фильтр по цене ====================

@router.callback_query(F.data == "search_price")
async def search_by_price(callback: CallbackQuery, lang: str = "ru"):
    """Показывает варианты диапазона цен."""
    await safe_edit_or_answer(
        callback,
        t("search_price_header", lang),
        reply_markup=get_price_range_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Поиск по продавцу ====================

@router.callback_query(F.data == "search_seller")
async def search_by_seller(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Начинает поиск по продавцу."""
    await state.set_state(SearchStates.waiting_for_seller)
    await state.update_data(
        search_query=None,
        search_category=None,
        search_min_price=None,
        search_max_price=None,
        search_location=None,
        search_page=1,
    )

    prompt_message = await safe_edit_or_answer(
        callback,
        t("search_seller_prompt", lang),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML",
    )
    await state.update_data(**{PROMPT_MESSAGE_ID: (prompt_message.message_id if prompt_message else callback.message.message_id)})
    await callback.answer()


@router.callback_query(F.data == "search_location")
async def search_by_location(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Начинает поиск по местоположению."""
    await state.set_state(SearchStates.waiting_for_location)
    await state.update_data(
        search_query=None,
        search_category=None,
        search_min_price=None,
        search_max_price=None,
        search_page=1,
    )

    prompt_message = await safe_edit_or_answer(
        callback,
        t("search_location_prompt", lang),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML",
    )
    await state.update_data(**{PROMPT_MESSAGE_ID: (prompt_message.message_id if prompt_message else callback.message.message_id)})
    await callback.answer()


@router.message(SearchStates.waiting_for_location)
async def process_location_search(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает ввод местоположения для поиска."""
    location = message.text.strip()

    if len(location) < 2:
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            t("search_query_too_short", lang),
            reply_markup=get_cancel_keyboard(lang),
        )
        return

    await state.update_data(search_location=location, search_page=1)
    await state.set_state(SearchStates.browsing_results)

    await show_search_results_message(message, state, lang)


@router.callback_query(F.data.startswith("price_range:"))
async def process_price_range(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Обрабатывает выбор диапазона цен."""
    range_str = callback.data.split(":")[1]

    if range_str == "custom":
        await state.set_state(SearchStates.waiting_for_min_price)
        prompt_message = await safe_edit_or_answer(
            callback,
            t("search_price_custom_min", lang),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )
        await state.update_data(**{PROMPT_MESSAGE_ID: (prompt_message.message_id if prompt_message else callback.message.message_id)})
        await callback.answer()
        return

    parts = range_str.split(":")
    min_price = float(parts[0]) if parts[0] != "0" else None
    max_price = float(parts[1]) if parts[1] != "0" else None

    await state.update_data(
        search_min_price=min_price,
        search_max_price=max_price,
        search_page=1,
    )
    await state.set_state(SearchStates.browsing_results)

    await show_search_results(callback, state, lang)


@router.message(SearchStates.waiting_for_min_price)
async def process_min_price(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает ввод минимальной цены."""
    is_valid, price, error = validate_price(message.text, lang)

    if not is_valid:
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            t("error_invalid_min_price", lang, error=error),
            reply_markup=get_cancel_keyboard(lang),
        )
        return

    await state.update_data(search_min_price=price if price > 0 else None)
    await state.set_state(SearchStates.waiting_for_max_price)

    await safe_send_or_edit_state_message(
        message,
        state,
        PROMPT_MESSAGE_ID,
        t("search_price_custom_max", lang),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(SearchStates.waiting_for_max_price)
async def process_max_price(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает ввод максимальной цены."""
    is_valid, price, error = validate_price(message.text, lang)

    if not is_valid:
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            t("error_invalid_max_price", lang, error=error),
            reply_markup=get_cancel_keyboard(lang),
        )
        return

    await state.update_data(
        search_max_price=price if price > 0 else None,
        search_page=1,
    )
    await state.set_state(SearchStates.browsing_results)

    await show_search_results_message(message, state, lang)


@router.message(SearchStates.waiting_for_seller)
async def process_seller_search(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает ввод продавца для поиска."""
    seller_input = message.text.strip()

    if len(seller_input) < 2:
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            t("search_query_too_short", lang),
            reply_markup=get_cancel_keyboard(lang),
        )
        return

    username = seller_input.lstrip("@")
    seller = await User.get_by_username(username)

    if not seller:
        seller = await User.search_by_display_name(seller_input)

    if not seller:
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            t("search_seller_not_found", lang, seller=escape_html(seller_input)),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="HTML",
        )
        return

    await state.update_data(
        search_seller_id=seller.id,
        search_seller_name=seller.display_name,
        search_page=1,
    )
    await state.set_state(SearchStates.browsing_results)

    await show_search_results_message(message, state, lang)


# ==================== Отмена и возврат к поиску ====================

@router.callback_query(F.data == "cancel", SearchStates.waiting_for_query)
@router.callback_query(F.data == "cancel", SearchStates.waiting_for_seller)
@router.callback_query(F.data == "cancel", SearchStates.waiting_for_location)
@router.callback_query(F.data == "cancel", SearchStates.waiting_for_min_price)
@router.callback_query(F.data == "cancel", SearchStates.waiting_for_max_price)
async def cancel_search_input(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Отменяет ввод поиска и возвращает меню поиска."""
    await state.clear()
    await safe_edit_or_answer(
        callback,
        t("search_menu", lang),
        reply_markup=get_search_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Результаты поиска ====================

async def show_search_results(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Показывает результаты поиска для callback-запросов."""
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

    if not listings:
        text += t("search_no_results", lang)
        await safe_edit_or_answer(
            callback,
            text,
            reply_markup=get_search_keyboard(lang),
            parse_mode="HTML",
        )
        await callback.answer()
        return

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

    await safe_edit_or_answer(callback, text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


async def show_search_results_message(message: Message, state: FSMContext, lang: str = "ru"):
    """Показывает результаты поиска для сообщений."""
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

    if not listings:
        text += t("search_no_results", lang)
        await safe_send_or_edit_state_message(
            message,
            state,
            PROMPT_MESSAGE_ID,
            text,
            reply_markup=get_search_keyboard(lang),
            parse_mode="HTML",
        )
        return

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

    await safe_send_or_edit_state_message(
        message,
        state,
        PROMPT_MESSAGE_ID,
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


# ==================== Пагинация ====================

@router.callback_query(F.data.startswith("search:page:"))
async def search_pagination(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Обрабатывает пагинацию поиска."""
    parts = callback.data.split(":")
    page = int(parts[2])
    extra_data = parts[3] if len(parts) > 3 else ""

    if extra_data:
        extra_parts = extra_data.split("|")
        query = extra_parts[0] if extra_parts[0] else None
        category = extra_parts[1] if len(extra_parts) > 1 and extra_parts[1] else None
        min_price = float(extra_parts[2]) if len(extra_parts) > 2 and extra_parts[2] else None
        max_price = float(extra_parts[3]) if len(extra_parts) > 3 and extra_parts[3] else None
        seller_id = int(extra_parts[4]) if len(extra_parts) > 4 and extra_parts[4] else None
        seller_name = extra_parts[5] if len(extra_parts) > 5 and extra_parts[5] else None
        location = extra_parts[6] if len(extra_parts) > 6 and extra_parts[6] else None

        await state.update_data(
            search_query=query,
            search_category=category,
            search_min_price=min_price,
            search_max_price=max_price,
            search_seller_id=seller_id,
            search_seller_name=seller_name,
            search_location=location,
        )

    await state.update_data(search_page=page)
    await show_search_results(callback, state, lang)


# ==================== Выбор категории из просмотра ====================

@router.callback_query(F.data.startswith("category:"))
async def category_from_main(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Обрабатывает выбор категории из основного просмотра."""
    category = callback.data.split(":")[1]

    await state.update_data(
        search_query=None,
        search_category=None if category == "all" else category,
        search_min_price=None,
        search_max_price=None,
        search_page=1,
    )
    await state.set_state(SearchStates.browsing_results)

    await show_search_results(callback, state, lang)
