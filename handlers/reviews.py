"""
Handlers for seller reviews and feedback.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from database.models import User, Listing, Review
from keyboards import (
    get_rating_keyboard,
    get_review_comment_keyboard,
    get_back_keyboard,
    get_cancel_keyboard,
    get_pagination_keyboard,
    get_confirm_keyboard,
)
from states import ReviewStates
from utils import format_review_text, escape_html
from utils.helpers import safe_edit_or_answer
from config import PAGE_SIZE
from i18n import t

logger = logging.getLogger(__name__)
router = Router(name="reviews")

REVIEWS_PER_PAGE = PAGE_SIZE


# ==================== Оставить отзыв ====================

@router.callback_query(F.data.startswith("leave_review:"))
async def leave_review(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Запускает сценарий отзыва о продавце объявления."""
    listing_id = int(callback.data.split(":")[1])

    user = await User.get_by_telegram_id(callback.from_user.id)
    listing = await Listing.get_by_id(listing_id, with_user=True)

    if not listing:
        await callback.answer(t("listing_not_found", lang), show_alert=True)
        return

    if listing.user_id == user.id:
        await callback.answer(t("cannot_review_self", lang), show_alert=True)
        return

    existing = await Review.get_by_reviewer_and_listing(user.id, listing_id)
    if existing:
        await callback.answer(t("already_reviewed", lang), show_alert=True)
        return

    await state.set_state(ReviewStates.waiting_for_rating)
    await state.update_data(listing_id=listing_id, seller_id=listing.user_id)

    seller_name = escape_html(listing.user.display_name) if listing.user else "..."

    await safe_edit_or_answer(
        callback,
        t("review_prompt", lang, seller=seller_name, title=escape_html(listing.title)),
        reply_markup=get_rating_keyboard(listing_id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Обработка оценки ====================

@router.callback_query(F.data.startswith("review_rating:"), ReviewStates.waiting_for_rating)
async def process_rating(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Обрабатывает выбор оценки звёздами."""
    parts = callback.data.split(":")
    rating = int(parts[1])
    listing_id = int(parts[2])

    await state.update_data(rating=rating, listing_id=listing_id)
    await state.set_state(ReviewStates.waiting_for_comment)

    stars = "⭐" * rating

    await safe_edit_or_answer(
        callback,
        t("rate_comment_prompt", lang, stars=stars, rating=rating),
        reply_markup=get_review_comment_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Обработка комментария ====================

@router.message(ReviewStates.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext, lang: str = "ru"):
    """Обрабатывает текст комментария к отзыву."""
    comment = message.text.strip() if message.text else None

    if comment and len(comment) > 500:
        await message.answer(
            t("comment_too_long", lang),
            reply_markup=get_review_comment_keyboard(lang),
        )
        return

    data = await state.get_data()
    await state.clear()

    user = await User.get_by_telegram_id(message.from_user.id)
    review = await Review.create(
        reviewer_id=user.id,
        seller_id=data["seller_id"],
        listing_id=data["listing_id"],
        rating=data["rating"],
        comment=comment,
    )

    if review:
        stars = "⭐" * data["rating"]
        text = t("review_saved", lang, stars=stars)
        if comment:
            text += t("review_with_comment", lang, comment=escape_html(comment))
        await message.answer(
            text,
            reply_markup=get_back_keyboard("back_to_menu", lang),
            parse_mode="HTML",
        )
        await _notify_seller_about_review(
            message.bot, data["seller_id"], data["listing_id"],
            data["rating"], comment, user.display_name, lang,
        )
    else:
        await message.answer(
            t("review_failed", lang),
            reply_markup=get_back_keyboard("back_to_menu", lang),
            parse_mode="HTML",
        )


# ==================== Пропуск комментария ====================

@router.callback_query(F.data == "skip_review_comment", ReviewStates.waiting_for_comment)
async def skip_comment(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Пропускает комментарий и сохраняет только оценку."""
    data = await state.get_data()
    await state.clear()

    user = await User.get_by_telegram_id(callback.from_user.id)
    review = await Review.create(
        reviewer_id=user.id,
        seller_id=data["seller_id"],
        listing_id=data["listing_id"],
        rating=data["rating"],
    )

    if review:
        stars = "⭐" * data["rating"]
        await safe_edit_or_answer(
            callback,
            t("review_saved", lang, stars=stars),
            reply_markup=get_back_keyboard("back_to_menu", lang),
            parse_mode="HTML",
        )
        await _notify_seller_about_review(
            callback.bot, data["seller_id"], data["listing_id"],
            data["rating"], None, user.display_name, lang,
        )
    else:
        await safe_edit_or_answer(
            callback,
            t("review_failed", lang),
            reply_markup=get_back_keyboard("back_to_menu", lang),
            parse_mode="HTML",
        )
    await callback.answer()


# ==================== Просмотр отзывов продавца ====================

@router.callback_query(F.data.startswith("seller_reviews:"))
async def view_seller_reviews(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Показывает отзывы о продавце с пагинацией."""
    parts = callback.data.split(":")

    if len(parts) == 4 and parts[1] == "page":
        page = int(parts[2])
        seller_id = int(parts[3])
    else:
        seller_id = int(parts[1])
        page = 1

    seller = await User.get_by_id(seller_id)
    if not seller:
        await callback.answer(t("seller_not_found", lang), show_alert=True)
        return

    total = await Review.count_by_seller(seller_id)

    if total == 0:
        await safe_edit_or_answer(
            callback,
            t("no_reviews", lang, seller=escape_html(seller.display_name)),
            reply_markup=get_back_keyboard("back_to_menu", lang),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    total_pages = (total + REVIEWS_PER_PAGE - 1) // REVIEWS_PER_PAGE
    offset = (page - 1) * REVIEWS_PER_PAGE

    reviews = await Review.get_by_seller(seller_id, limit=REVIEWS_PER_PAGE, offset=offset)

    current_user = await User.get_by_telegram_id(callback.from_user.id)

    avg_rating = seller.rating
    text = t(
        "seller_reviews_header", lang,
        seller=escape_html(seller.display_name),
        stars="⭐" * round(avg_rating),
        rating=avg_rating,
        total=total,
    )

    for review in reviews:
        reviewer = await User.get_by_id(review.reviewer_id)
        text += format_review_text(review, reviewer, lang) + "\n"

    builder = InlineKeyboardBuilder()

    for review in reviews:
        if current_user and review.reviewer_id == current_user.id:
            builder.row(
                InlineKeyboardButton(
                    text=t("btn_delete_my_review", lang),
                    callback_data=f"delete_review:{review.id}:{seller_id}",
                )
            )

    if total_pages > 1:
        nav_buttons = []
        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=t("btn_prev", lang),
                    callback_data=f"seller_reviews:page:{page - 1}:{seller_id}",
                )
            )
        nav_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
        if page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=t("btn_next", lang),
                    callback_data=f"seller_reviews:page:{page + 1}:{seller_id}",
                )
            )
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(text=t("btn_back_to_menu", lang), callback_data="back_to_menu")
    )

    await safe_edit_or_answer(
        callback,
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Удаление отзыва пользователем ====================

@router.callback_query(F.data.startswith("delete_review:"))
async def delete_review_confirm(callback: CallbackQuery, lang: str = "ru"):
    """Запрашивает подтверждение перед удалением своего отзыва."""
    parts = callback.data.split(":")
    review_id = int(parts[1])
    seller_id = int(parts[2])

    review = await Review.get_by_id(review_id)
    if not review:
        await callback.answer(t("review_not_found", lang), show_alert=True)
        return

    current_user = await User.get_by_telegram_id(callback.from_user.id)
    if not current_user or review.reviewer_id != current_user.id:
        await callback.answer(t("cannot_delete_others_review", lang), show_alert=True)
        return

    stars = "⭐" * review.rating
    text = t("delete_review_confirm", lang, stars=stars)
    if review.comment:
        text += t("delete_review_comment_line", lang, comment=escape_html(review.comment))
    text += t("delete_review_question", lang)

    await safe_edit_or_answer(
        callback,
        text,
        reply_markup=get_confirm_keyboard(
            confirm_callback=f"confirm_delete_review:{review_id}:{seller_id}",
            cancel_callback=f"seller_reviews:{seller_id}",
            lang=lang,
        ),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_review:"))
async def confirm_delete_review(callback: CallbackQuery, lang: str = "ru"):
    """Удаляет отзыв после подтверждения."""
    parts = callback.data.split(":")
    review_id = int(parts[1])
    seller_id = int(parts[2])

    review = await Review.get_by_id(review_id)
    if not review:
        await callback.answer(t("review_not_found", lang), show_alert=True)
        return

    current_user = await User.get_by_telegram_id(callback.from_user.id)
    if not current_user or review.reviewer_id != current_user.id:
        await callback.answer(t("cannot_delete_others_review", lang), show_alert=True)
        return

    success = await Review.delete(review_id, seller_id)

    if success:
        await safe_edit_or_answer(
            callback,
            t("review_deleted", lang),
            reply_markup=get_back_keyboard(f"seller_reviews:{seller_id}", lang),
            parse_mode="HTML",
        )
    else:
        await safe_edit_or_answer(
            callback,
            t("review_delete_failed", lang),
            reply_markup=get_back_keyboard(f"seller_reviews:{seller_id}", lang),
            parse_mode="HTML",
        )
    await callback.answer()


# ==================== Уведомления ====================

async def _notify_seller_about_review(
    bot, seller_id: int, listing_id: int, rating: int,
    comment: str | None, reviewer_name: str, lang: str = "ru",
):
    """Отправляет продавцу уведомление о новом отзыве."""
    try:
        seller = await User.get_by_id(seller_id)
        if not seller:
            return

        listing = await Listing.get_by_id(listing_id)
        listing_title = (
            escape_html(listing.title) if listing
            else t("listing_title_fallback", lang)
        )

        stars = "⭐" * rating
        text = t(
            "new_review_notification", lang,
            reviewer=escape_html(reviewer_name),
            listing=listing_title,
            stars=stars,
            rating=rating,
        )
        if comment:
            text += t("new_review_comment", lang, comment=escape_html(comment))

        await bot.send_message(seller.telegram_id, text, parse_mode="HTML")
    except Exception as e:
        logger.warning(f"Failed to notify seller {seller_id} about review: {e}")
