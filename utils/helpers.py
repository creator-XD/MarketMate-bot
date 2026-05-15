"""
Вспомогательные функции Telegram Marketplace Bot.
"""
from __future__ import annotations

import html
import logging
from typing import Optional, TYPE_CHECKING
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from config import CURRENCY
from i18n import t, get_category_name, get_category_emoji  # noqa: F401 (реэкспорт)

if TYPE_CHECKING:
    from database.models import Listing, User

logger = logging.getLogger(__name__)


def escape_html(text: str) -> str:
    """Экранирует специальные символы HTML."""
    if text is None:
        return ""
    return html.escape(str(text))


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Обрезает текст до заданной длины."""
    if text is None:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_price(price: Optional[float], currency: str = CURRENCY) -> str:
    """Форматирует цену для пользовательских сообщений."""
    if price is None:
        return "Цена не указана"

    amount = float(price)
    if amount.is_integer():
        formatted = f"{int(amount):,}"
    else:
        formatted = f"{amount:,.2f}".rstrip("0").rstrip(".")

    return f"{formatted.replace(',', ' ')} {currency}"


def format_listing_text(
    listing: Listing,
    user: Optional[User] = None,
    detailed: bool = True,
    lang: str = "ru",
) -> str:
    """
    Форматирует объявление для сообщения Telegram.

    Аргументы:
        listing: объявление для форматирования
        user: необязательный объект пользователя-продавца
        detailed: показывать ли подробности
        lang: код языка ('ru' или 'en')

    Возвращает:
        Отформатированная HTML-строка
    """
    category_name = get_category_name(listing.category, lang)
    price_text = format_price(listing.price)

    if detailed:
        text = f"\n<b>{escape_html(listing.title)}</b>\n\n"
        text += t("listing_price_label", lang, price=price_text) + "\n"
        text += t("listing_category_label", lang, category=category_name) + "\n"

        condition_name = t(f"condition_{listing.condition}", lang) if listing.condition else t("condition_new", lang)
        text += t("listing_condition_label", lang, condition=condition_name) + "\n"

        if listing.location:
            text += t("listing_location_label", lang, location=escape_html(listing.location)) + "\n"

        description = escape_html(listing.description) if listing.description else t("no_description", lang)
        text += "\n" + t("listing_description_label", lang, description=description) + "\n"

        if user:
            text += t("listing_seller_label", lang, name=escape_html(user.display_name))
            if user.rating > 0:
                text += t("listing_seller_rating", lang, rating=user.rating, count=user.rating_count)

        text += t("listing_views_label", lang, views=listing.views)

        if listing.status != "active":
            status_emoji = "✅" if listing.status == "sold" else "🔒"
            status_text = t("status_sold_text", lang) if listing.status == "sold" else listing.status.title()
            text += t("listing_status_label", lang, emoji=status_emoji, status=status_text)
    else:
        # Краткий формат
        text = f"<b>{escape_html(truncate_text(listing.title, 40))}</b>\n"
        text += f"💰 {price_text} | 📁 {category_name}"

    return text


def format_listing_short(listing: Listing) -> str:
    """Форматирует объявление в краткую однострочную запись."""
    price_text = format_price(listing.price)
    title = truncate_text(listing.title, 30)
    return f"{title} - {price_text}"


def format_user_profile(user: User, lang: str = "ru") -> str:
    """Форматирует профиль пользователя для отображения."""
    text = t("profile_header_text", lang)
    text += t("profile_name_label", lang, name=escape_html(user.display_name))

    if user.username:
        text += t("profile_username_label", lang, username=escape_html(user.username))

    if user.phone:
        text += t("profile_phone_label", lang, phone=escape_html(user.phone))

    if user.location:
        text += t("profile_location_label", lang, location=escape_html(user.location))

    if user.bio:
        text += t("profile_bio_label", lang, bio=escape_html(user.bio))

    if user.rating > 0:
        text += t("profile_rating_label", lang, rating=user.rating, count=user.rating_count)

    if user.is_verified:
        text += t("profile_verified", lang)

    return text


def format_review_text(review, reviewer: Optional[User] = None, lang: str = "ru") -> str:
    """Форматирует один отзыв для отображения."""
    stars = "⭐" * review.rating
    reviewer_name = (
        escape_html(reviewer.display_name)
        if reviewer
        else t("reviewer_unknown", lang, id=review.reviewer_id)
    )
    text = f"{stars}\n"
    text += f"<b>{reviewer_name}</b>"
    if review.created_at:
        date_str = str(review.created_at)[:10]
        text += f" — {date_str}"
    text += "\n"
    if review.comment:
        text += f"{escape_html(review.comment)}\n"
    return text


def format_search_results_header(
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    seller_name: Optional[str] = None,
    location: Optional[str] = None,
    total: int = 0,
    lang: str = "ru",
) -> str:
    """Форматирует заголовок результатов поиска."""
    text = t("search_results_header", lang)

    filters = []
    if query:
        filters.append(t("search_keywords_filter", lang, query=escape_html(query)))
    if category and category != "all":
        filters.append(t("search_category_filter", lang, category=get_category_name(category, lang)))
    if seller_name:
        filters.append(t("search_seller_filter", lang, seller=escape_html(seller_name)))
    if location:
        filters.append(t("search_location_filter", lang, location=escape_html(location)))
    if min_price is not None or max_price is not None:
        if min_price and max_price:
            filters.append(t("search_price_both", lang, min=format_price(min_price), max=format_price(max_price)))
        elif min_price:
            filters.append(t("search_price_from", lang, min=format_price(min_price)))
        elif max_price:
            filters.append(t("search_price_to", lang, max=format_price(max_price)))

    if filters:
        text += t("search_filters_label", lang, filters=", ".join(filters))

    text += t("search_total_found", lang, total=total)

    return text


def validate_price(text: str, lang: str = "ru") -> tuple[bool, Optional[float], str]:
    """
    Проверяет введённую цену.

    Возвращает:
        Кортеж (is_valid, price_value, error_message)
    """
    try:
        cleaned = (
            text.strip()
            .lower()
            .replace("$", "")
            .replace("₽", "")
            .replace("руб.", "")
            .replace("руб", "")
            .replace(",", "")
            .replace(" ", "")
        )
        price = float(cleaned)

        if price < 0:
            return False, None, t("validate_price_negative", lang)

        if price > 1000000:
            return False, None, t("validate_price_too_high", lang)

        return True, round(price, 2), ""
    except ValueError:
        return False, None, t("validate_price_invalid", lang)


def validate_title(text: str, lang: str = "ru") -> tuple[bool, str]:
    """
    Проверяет название объявления.

    Возвращает:
        Кортеж (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, t("validate_title_empty", lang)

    if len(text.strip()) < 3:
        return False, t("validate_title_too_short", lang)

    if len(text.strip()) > 100:
        return False, t("validate_title_too_long", lang)

    return True, ""


def validate_description(text: str, lang: str = "ru") -> tuple[bool, str]:
    """
    Проверяет описание объявления.

    Возвращает:
        Кортеж (is_valid, error_message)
    """
    if text and len(text.strip()) > 2000:
        return False, t("validate_description_too_long", lang)

    return True, ""


def _telegram_error_text(error: Exception) -> str:
    return str(error).lower()


def _is_ignored_delete_error(error: Exception) -> bool:
    error_text = _telegram_error_text(error)
    ignored_fragments = (
        "message to delete not found",
        "message can't be deleted",
        "message can not be deleted",
        "message not found",
        "chat not found",
    )
    return any(fragment in error_text for fragment in ignored_fragments)


def _is_ignored_edit_error(error: Exception) -> bool:
    error_text = _telegram_error_text(error)
    ignored_fragments = (
        "message is not modified",
        "message to edit not found",
        "message can't be edited",
        "message can not be edited",
        "there is no text in the message to edit",
        "message to delete not found",
        "message not found",
        "chat not found",
    )
    return any(fragment in error_text for fragment in ignored_fragments)


async def safe_delete_message(bot, chat_id: int, message_id: Optional[int]) -> bool:
    """Safely deletes a Telegram message and ignores stale message ids."""
    if not message_id:
        return False

    try:
        await bot.delete_message(chat_id, message_id)
        return True
    except TelegramBadRequest as e:
        if not _is_ignored_delete_error(e):
            logger.warning("Failed to delete message %s in chat %s: %s", message_id, chat_id, e)
    except TelegramForbiddenError as e:
        logger.warning("Forbidden to delete message %s in chat %s: %s", message_id, chat_id, e)
    except Exception as e:
        logger.exception("Unexpected error deleting message %s in chat %s: %s", message_id, chat_id, e)
    return False


async def safe_edit_message_text(
    bot,
    chat_id: int,
    message_id: Optional[int],
    text: str,
    reply_markup=None,
    parse_mode: Optional[str] = None,
    **kwargs,
) -> bool:
    """Safely edits a Telegram text message and treats no-op edits as success."""
    if not message_id:
        return False

    params = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": reply_markup,
        **kwargs,
    }
    if parse_mode is not None:
        params["parse_mode"] = parse_mode

    try:
        await bot.edit_message_text(text, **params)
        return True
    except TelegramBadRequest as e:
        if "message is not modified" in _telegram_error_text(e):
            return True
        if not _is_ignored_edit_error(e):
            logger.warning("Failed to edit message %s in chat %s: %s", message_id, chat_id, e)
    except TelegramForbiddenError as e:
        logger.warning("Forbidden to edit message %s in chat %s: %s", message_id, chat_id, e)
    except Exception as e:
        logger.exception("Unexpected error editing message %s in chat %s: %s", message_id, chat_id, e)
    return False


async def safe_clear_reply_markup(bot, chat_id: int, message_id: Optional[int]) -> bool:
    """Safely removes inline buttons from a Telegram message."""
    if not message_id:
        return False

    try:
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
        return True
    except TelegramBadRequest as e:
        if "message is not modified" in _telegram_error_text(e):
            return True
        if not _is_ignored_edit_error(e):
            logger.warning("Failed to clear reply markup for message %s in chat %s: %s", message_id, chat_id, e)
    except TelegramForbiddenError as e:
        logger.warning("Forbidden to clear reply markup for message %s in chat %s: %s", message_id, chat_id, e)
    except Exception as e:
        logger.exception(
            "Unexpected error clearing reply markup for message %s in chat %s: %s",
            message_id,
            chat_id,
            e,
        )
    return False


async def safe_send_or_edit_state_message(
    message,
    state,
    state_key: str,
    text: str,
    reply_markup=None,
    parse_mode: Optional[str] = None,
    **kwargs,
):
    """Edits a stored FSM service message or sends one and stores its message_id."""
    data = await state.get_data()
    message_id = data.get(state_key)

    if message_id:
        edited = await safe_edit_message_text(
            message.bot,
            message.chat.id,
            message_id,
            text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            **kwargs,
        )
        if edited:
            return None

        await safe_delete_message(message.bot, message.chat.id, message_id)

    send_params = {
        "reply_markup": reply_markup,
        **kwargs,
    }
    if parse_mode is not None:
        send_params["parse_mode"] = parse_mode

    sent_message = await message.answer(text, **send_params)
    await state.update_data(**{state_key: sent_message.message_id})
    return sent_message


async def safe_delete_state_message(bot, chat_id: int, state, state_key: str) -> bool:
    """Deletes a stored FSM service message and removes its id from FSM data."""
    data = await state.get_data()
    message_id = data.pop(state_key, None)
    if message_id is not None:
        await state.set_data(data)
    return await safe_delete_message(bot, chat_id, message_id)


async def safe_edit_or_answer(callback_query, text: str, **kwargs):
    """
    Безопасно редактирует сообщение или отправляет новое при ошибке редактирования.

    Обрабатывает случаи, когда callback пришёл из сообщения с фотографией
    где edit_text() завершился бы ошибкой.

    Аргументы:
        callback_query: объект CallbackQuery
        text: текст для отправки
        **kwargs: дополнительные параметры вроде reply_markup, parse_mode и т. д.
    """
    message = callback_query.message
    if not message:
        return None

    try:
        return await message.edit_text(text, **kwargs)
    except TelegramBadRequest as e:
        if "message is not modified" in _telegram_error_text(e):
            return message
        if not _is_ignored_edit_error(e):
            logger.warning(
                "Failed to edit callback message %s in chat %s: %s",
                message.message_id,
                message.chat.id,
                e,
            )
    except TelegramForbiddenError as e:
        logger.warning(
            "Forbidden to edit callback message %s in chat %s: %s",
            message.message_id,
            message.chat.id,
            e,
        )
    except Exception as e:
        logger.exception(
            "Unexpected error editing callback message %s in chat %s: %s",
            message.message_id,
            message.chat.id,
            e,
        )

    await safe_clear_reply_markup(message.bot, message.chat.id, message.message_id)
    await safe_delete_message(message.bot, message.chat.id, message.message_id)

    try:
        return await message.answer(text, **kwargs)
    except Exception as e:
        logger.exception("Failed to send fallback message in chat %s: %s", message.chat.id, e)
        return None
