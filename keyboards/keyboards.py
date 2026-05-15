"""
Inline- и reply-клавиатуры Telegram Marketplace Bot.
Все функции клавиатур принимают необязательный параметр `lang` (по умолчанию "ru").
"""
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import List, Optional
from i18n import t, get_category_name, CATEGORY_KEYS, CATEGORY_EMOJIS
from utils.helpers import format_price


def get_main_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает inline-клавиатуру главного меню."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=t("btn_browse", lang), callback_data="browse"),
        InlineKeyboardButton(text=t("btn_search", lang), callback_data="search"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_my_listings", lang), callback_data="my_listings"),
        InlineKeyboardButton(text=t("btn_favorites", lang), callback_data="favorites"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_add_listing", lang), callback_data="add_listing"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_my_profile", lang), callback_data="profile"),
        InlineKeyboardButton(text=t("btn_help", lang), callback_data="help"),
    )

    return builder.as_markup()


def get_categories_keyboard(
    callback_prefix: str = "category",
    include_all: bool = True,
    include_back: bool = True,
    back_callback: str = "back_to_menu",
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру выбора категории."""
    builder = InlineKeyboardBuilder()

    if include_all:
        builder.row(
            InlineKeyboardButton(
                text=t("btn_all_categories", lang),
                callback_data=f"{callback_prefix}:all",
            )
        )

    # Формируем список категорий на выбранном языке
    categories = [
        {"id": cat_id, "name": t(key, lang), "emoji": CATEGORY_EMOJIS[cat_id]}
        for cat_id, key in CATEGORY_KEYS.items()
    ]

    for i in range(0, len(categories), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(categories):
                cat = categories[i + j]
                row_buttons.append(
                    InlineKeyboardButton(
                        text=cat["name"],
                        callback_data=f"{callback_prefix}:{cat['id']}",
                    )
                )
        builder.row(*row_buttons)

    if include_back:
        builder.row(
            InlineKeyboardButton(text=t("btn_back", lang), callback_data=back_callback)
        )

    return builder.as_markup()


def get_listing_actions_keyboard(
    listing_id: int,
    is_owner: bool = False,
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру действий для объявления."""
    builder = InlineKeyboardBuilder()

    if is_owner:
        builder.row(
            InlineKeyboardButton(text=t("btn_edit", lang), callback_data=f"edit_listing:{listing_id}"),
            InlineKeyboardButton(text=t("btn_delete", lang), callback_data=f"delete_listing:{listing_id}"),
        )
        builder.row(
            InlineKeyboardButton(text=t("btn_mark_sold", lang), callback_data=f"mark_sold:{listing_id}"),
        )
    else:
        builder.row(
            InlineKeyboardButton(text=t("btn_contact_seller", lang), callback_data=f"contact_seller:{listing_id}"),
        )
        builder.row(
            InlineKeyboardButton(text=t("btn_add_to_favorites", lang), callback_data=f"add_favorite:{listing_id}"),
        )

    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="back_to_listings"),
    )

    return builder.as_markup()


def get_my_listings_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает клавиатуру меню моих объявлений."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=t("btn_active_listings", lang), callback_data="my_active"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_sold_listings", lang), callback_data="my_sold"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_add_listing", lang), callback_data="add_listing"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back_to_menu", lang), callback_data="back_to_menu"),
    )

    return builder.as_markup()


def get_search_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает клавиатуру вариантов поиска."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=t("btn_search_keywords", lang), callback_data="search_keywords"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_search_categories", lang), callback_data="search_category"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_search_price", lang), callback_data="search_price"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_search_seller", lang), callback_data="search_seller"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_search_location", lang), callback_data="search_location"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back_to_menu", lang), callback_data="back_to_menu"),
    )

    return builder.as_markup()


def get_confirm_keyboard(
    confirm_callback: str,
    cancel_callback: str = "cancel",
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру подтверждения."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=t("btn_confirm", lang), callback_data=confirm_callback),
        InlineKeyboardButton(text=t("btn_cancel", lang), callback_data=cancel_callback),
    )

    return builder.as_markup()


def get_cancel_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает клавиатуру отмены."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel"),
    )
    return builder.as_markup()


def get_back_keyboard(callback_data: str = "back_to_menu", lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с кнопкой назад."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data=callback_data),
    )
    return builder.as_markup()


def get_report_listing_keyboard(listing_id: int, seller_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура выбора причины жалобы на объявление."""
    builder = InlineKeyboardBuilder()
    reasons = ["spam", "fraud", "inappropriate", "wrong_category", "other"]
    for reason in reasons:
        builder.row(
            InlineKeyboardButton(
                text=t(f"btn_report_reason_{reason}", lang),
                callback_data=f"report_reason:listing:{listing_id}:{reason}",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_report_user", lang),
            callback_data=f"report_user:{seller_id}",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel")
    )
    return builder.as_markup()


def get_report_user_keyboard(user_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура выбора причины жалобы на пользователя."""
    builder = InlineKeyboardBuilder()
    reasons = ["spam", "scam", "abuse", "other"]
    for reason in reasons:
        builder.row(
            InlineKeyboardButton(
                text=t(f"btn_report_reason_{reason}", lang),
                callback_data=f"report_reason:user:{user_id}:{reason}",
            )
        )
    builder.row(
        InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel")
    )
    return builder.as_markup()


def get_report_comment_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура при запросе необязательного комментария."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_skip_report_comment", lang),
            callback_data="skip_report_comment",
        ),
        InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel"),
    )
    return builder.as_markup()


def get_new_message_keyboard(buyer_id: int, listing_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура продавцу при новом сообщении покупателя с кнопкой ответа."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_reply_to_buyer", lang),
            callback_data=f"reply_to_buyer:{buyer_id}:{listing_id}",
        )
    )
    return builder.as_markup()


def get_seller_replied_keyboard(listing_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура покупателю при ответе продавца с кнопкой повторного сообщения."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_reply_to_seller", lang),
            callback_data=f"contact_seller:{listing_id}",
        )
    )
    return builder.as_markup()


def get_condition_keyboard(callback_prefix: str = "listing_condition", lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает клавиатуру выбора состояния товара."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_condition_new", lang), callback_data=f"{callback_prefix}:new"),
        InlineKeyboardButton(text=t("btn_condition_used", lang), callback_data=f"{callback_prefix}:used"),
        InlineKeyboardButton(text=t("btn_condition_good", lang), callback_data=f"{callback_prefix}:good"),
    )
    return builder.as_markup()


def get_skip_keyboard(skip_callback: str = "skip", lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с кнопкой пропуска."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_skip", lang), callback_data=skip_callback),
        InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel"),
    )
    return builder.as_markup()


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str,
    extra_data: str = "",
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру пагинации."""
    builder = InlineKeyboardBuilder()

    row_buttons = []

    if current_page > 1:
        row_buttons.append(
            InlineKeyboardButton(
                text=t("btn_prev", lang),
                callback_data=f"{callback_prefix}:page:{current_page - 1}:{extra_data}",
            )
        )

    row_buttons.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total_pages}",
            callback_data="noop",
        )
    )

    if current_page < total_pages:
        row_buttons.append(
            InlineKeyboardButton(
                text=t("btn_next", lang),
                callback_data=f"{callback_prefix}:page:{current_page + 1}:{extra_data}",
            )
        )

    builder.row(*row_buttons)
    builder.row(
        InlineKeyboardButton(text=t("btn_back_to_menu", lang), callback_data="back_to_menu"),
    )

    return builder.as_markup()


def get_listing_detail_keyboard(
    listing_id: int,
    is_owner: bool = False,
    is_favorite: bool = False,
    seller_id: int = None,
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру подробного просмотра объявления."""
    builder = InlineKeyboardBuilder()

    if is_owner:
        builder.row(
            InlineKeyboardButton(text=t("btn_edit", lang), callback_data=f"edit_listing:{listing_id}"),
            InlineKeyboardButton(text=t("btn_delete", lang), callback_data=f"delete_listing:{listing_id}"),
        )
        builder.row(
            InlineKeyboardButton(text=t("btn_mark_sold", lang), callback_data=f"mark_sold:{listing_id}"),
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text=t("btn_contact_seller", lang),
                callback_data=f"contact_seller:{listing_id}",
            ),
        )

        fav_text = t("btn_remove_from_favorites", lang) if is_favorite else t("btn_add_to_favorites", lang)
        fav_callback = f"remove_favorite:{listing_id}" if is_favorite else f"add_favorite:{listing_id}"
        builder.row(
            InlineKeyboardButton(text=fav_text, callback_data=fav_callback),
        )
        builder.row(
            InlineKeyboardButton(text=t("btn_leave_review", lang), callback_data=f"leave_review:{listing_id}"),
        )
        if seller_id is not None:
            builder.row(
                InlineKeyboardButton(
                    text=t("btn_report_listing", lang),
                    callback_data=f"report_listing:{listing_id}",
                )
            )

    if seller_id is not None and not is_owner:
        builder.row(
            InlineKeyboardButton(
                text=t("btn_seller_listings", lang),
                callback_data=f"seller_listings:{seller_id}",
            ),
            InlineKeyboardButton(
                text=t("btn_seller_reviews", lang),
                callback_data=f"seller_reviews:{seller_id}",
            ),
        )
    elif seller_id is not None:
        builder.row(
            InlineKeyboardButton(
                text=t("btn_seller_reviews", lang),
                callback_data=f"seller_reviews:{seller_id}",
            ),
        )

    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="back_to_listings"),
    )

    return builder.as_markup()


def get_edit_listing_keyboard(listing_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает клавиатуру вариантов редактирования объявления."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=t("btn_edit_title", lang), callback_data=f"edit_field:title:{listing_id}"),
        InlineKeyboardButton(text=t("btn_edit_description", lang), callback_data=f"edit_field:description:{listing_id}"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_edit_price", lang), callback_data=f"edit_field:price:{listing_id}"),
        InlineKeyboardButton(text=t("btn_edit_category", lang), callback_data=f"edit_field:category:{listing_id}"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_edit_condition", lang), callback_data=f"edit_field:condition:{listing_id}"),
        InlineKeyboardButton(text=t("btn_edit_photos", lang), callback_data=f"edit_field:photos:{listing_id}"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data=f"view_listing:{listing_id}"),
    )

    return builder.as_markup()


def get_listings_keyboard(
    listings: List,
    callback_prefix: str = "view_listing",
    show_price: bool = True,
) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с кнопками объявлений."""
    builder = InlineKeyboardBuilder()

    for listing in listings:
        text = listing.title[:30]
        if show_price:
            text += f" - {format_price(listing.price)}"
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"{callback_prefix}:{listing.id}",
            )
        )

    return builder.as_markup()


def get_price_range_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает предустановленные диапазоны цен."""
    builder = InlineKeyboardBuilder()

    ranges = [
        (t("price_range_0_25", lang), "0:25"),
        (t("price_range_25_50", lang), "25:50"),
        (t("price_range_50_100", lang), "50:100"),
        (t("price_range_100_500", lang), "100:500"),
        (t("price_range_500plus", lang), "500:0"),
        (t("price_range_custom", lang), "custom"),
    ]

    for i in range(0, len(ranges), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(ranges):
                text, data = ranges[i + j]
                row_buttons.append(
                    InlineKeyboardButton(text=text, callback_data=f"price_range:{data}")
                )
        builder.row(*row_buttons)

    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="search"),
    )

    return builder.as_markup()


def get_done_keyboard(done_callback: str = "done", lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с кнопкой готовности для множественного выбора, например фото."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_done", lang), callback_data=done_callback),
        InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel"),
    )
    return builder.as_markup()


def get_share_contact_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Возвращает клавиатуру для отправки контакта."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=t("btn_share_contact", lang), request_contact=True))
    builder.row(KeyboardButton(text=t("btn_skip", lang)))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_share_location_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Возвращает клавиатуру для отправки местоположения."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=t("btn_share_location", lang), request_location=True))
    builder.row(KeyboardButton(text=t("btn_skip", lang)))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_rating_keyboard(listing_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает клавиатуру оценки звёздами от 1 до 5."""
    builder = InlineKeyboardBuilder()
    stars = []
    for i in range(1, 6):
        stars.append(
            InlineKeyboardButton(
                text="⭐" * i,
                callback_data=f"review_rating:{i}:{listing_id}",
            )
        )
    builder.row(stars[0], stars[1])
    builder.row(stars[2], stars[3])
    builder.row(stars[4])
    builder.row(
        InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel"),
    )
    return builder.as_markup()


def get_review_comment_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает клавиатуру шага комментария к отзыву с пропуском или отменой."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_skip", lang), callback_data="skip_review_comment"),
        InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel"),
    )
    return builder.as_markup()


def get_seller_reviews_keyboard(seller_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Возвращает кнопку просмотра всех отзывов продавца."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_seller_reviews", lang),
            callback_data=f"seller_reviews:{seller_id}",
        ),
    )
    return builder.as_markup()


def remove_keyboard() -> ReplyKeyboardRemove:
    """Убирает reply-клавиатуру."""
    return ReplyKeyboardRemove()
