"""
Обработчики общения покупателя и продавца.
"""
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models import User, Listing, Message as DBMessage
from keyboards import get_cancel_keyboard, get_main_menu_keyboard, get_new_message_keyboard, get_seller_replied_keyboard
from states import MessageStates
from utils import format_listing_short, escape_html, format_price
from utils.helpers import safe_edit_or_answer
from i18n import t

logger = logging.getLogger(__name__)
router = Router(name="messages")


@router.callback_query(F.data.startswith("contact_seller:"))
async def contact_seller(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Запускает сценарий связи с продавцом."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id, with_user=True)

    if not listing:
        await callback.answer(t("listing_not_found", lang), show_alert=True)
        return

    user = await User.get_by_telegram_id(callback.from_user.id)
    if listing.user_id == user.id:
        await callback.answer(t("cannot_message_self", lang), show_alert=True)
        return

    await state.set_state(MessageStates.waiting_for_message)
    await state.update_data(
        contact_listing_id=listing_id,
        contact_seller_id=listing.user_id,
        contact_seller_telegram_id=listing.user.telegram_id,
    )

    await safe_edit_or_answer(
        callback,
        t("contact_seller_header", lang,
          title=escape_html(listing.title),
          seller=escape_html(listing.user.display_name)),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(MessageStates.waiting_for_message)
async def process_buyer_message(message: Message, state: FSMContext, bot: Bot, lang: str = "ru"):
    """Обрабатывает и отправляет сообщение продавцу."""
    if not message.text or len(message.text.strip()) < 2:
        await message.answer(t("message_too_short", lang), reply_markup=get_cancel_keyboard(lang))
        return

    if len(message.text) > 1000:
        await message.answer(t("message_too_long", lang), reply_markup=get_cancel_keyboard(lang))
        return

    data = await state.get_data()
    listing_id = data["contact_listing_id"]
    seller_telegram_id = data["contact_seller_telegram_id"]
    seller_id = data["contact_seller_id"]

    listing = await Listing.get_by_id(listing_id)
    buyer = await User.get_by_telegram_id(message.from_user.id)

    if not listing:
        await state.clear()
        await message.answer(t("listing_not_exists", lang), reply_markup=get_main_menu_keyboard(lang))
        return

    seller = await User.get_by_id(seller_id)

    await DBMessage.create(
        sender_id=buyer.id,
        receiver_id=seller_id,
        listing_id=listing_id,
        message_text=message.text.strip(),
    )

    seller_lang = seller.language if seller else "ru"
    username_part = f" (@{buyer.username})" if buyer.username else ""
    seller_message = t(
        "seller_notification", seller_lang,
        buyer=escape_html(buyer.display_name),
        username_part=username_part,
        title=escape_html(listing.title),
        price=format_price(listing.price),
        text=escape_html(message.text.strip()),
    )

    try:
        await bot.send_message(
            seller_telegram_id,
            seller_message,
            parse_mode="HTML",
            reply_markup=get_new_message_keyboard(buyer.id, listing_id, seller_lang),
        )

        await state.clear()

        response_text = t("message_sent_success", lang)

        if seller and seller.username:
            response_text += t("contact_seller_direct", lang, username=seller.username)
        else:
            response_text += t("seller_will_reply", lang)

        await message.answer(response_text, reply_markup=get_main_menu_keyboard(lang), parse_mode="HTML")

        logger.info(f"Message sent: buyer {buyer.telegram_id} -> seller {seller_telegram_id} for listing {listing_id}")

    except Exception as e:
        logger.error(f"Failed to send message to seller: {e}")
        await state.clear()
        await message.answer(t("message_failed", lang), reply_markup=get_main_menu_keyboard(lang), parse_mode="HTML")


# ==================== Ответ покупателю (для будущего расширения) ====================

@router.callback_query(F.data.startswith("reply_to_buyer:"))
async def reply_to_buyer(callback: CallbackQuery, state: FSMContext, lang: str = "ru"):
    """Запускает сценарий ответа покупателю."""
    parts = callback.data.split(":")
    buyer_id = int(parts[1])
    listing_id = int(parts[2]) if len(parts) > 2 else None

    await state.set_state(MessageStates.waiting_for_reply)
    await state.update_data(reply_buyer_id=buyer_id, reply_listing_id=listing_id)

    await safe_edit_or_answer(
        callback,
        t("reply_to_buyer_prompt", lang),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(MessageStates.waiting_for_reply)
async def process_seller_reply(message: Message, state: FSMContext, bot: Bot, lang: str = "ru"):
    """Обрабатывает ответ продавца покупателю."""
    if not message.text or len(message.text.strip()) < 2:
        await message.answer(t("reply_too_short", lang), reply_markup=get_cancel_keyboard(lang))
        return

    data = await state.get_data()
    buyer_id = data.get("reply_buyer_id")
    listing_id = data.get("reply_listing_id")

    buyer = await User.get_by_id(buyer_id)
    seller = await User.get_by_telegram_id(message.from_user.id)

    if not buyer:
        await state.clear()
        await message.answer(t("buyer_not_found", lang), reply_markup=get_main_menu_keyboard(lang))
        return

    await DBMessage.create(
        sender_id=seller.id,
        receiver_id=buyer_id,
        listing_id=listing_id,
        message_text=message.text.strip(),
    )

    buyer_lang = buyer.language if buyer else "ru"
    username_part = f" (@{seller.username})" if seller.username else ""
    reply_text = t(
        "seller_reply_notification", buyer_lang,
        seller=escape_html(seller.display_name),
        username_part=username_part,
    )

    listing = None
    if listing_id:
        listing = await Listing.get_by_id(listing_id)
        if listing:
            reply_text += t("seller_reply_listing_part", buyer_lang, title=escape_html(listing.title))

    reply_text += t("seller_reply_message_part", buyer_lang, text=escape_html(message.text.strip()))

    buyer_keyboard = get_seller_replied_keyboard(listing_id, buyer_lang) if listing_id else get_main_menu_keyboard(buyer_lang)

    try:
        await bot.send_message(buyer.telegram_id, reply_text, parse_mode="HTML", reply_markup=buyer_keyboard)

        await state.clear()
        await message.answer(t("reply_sent", lang), reply_markup=get_main_menu_keyboard(lang), parse_mode="HTML")

    except Exception as e:
        logger.error(f"Failed to send reply to buyer: {e}")
        await state.clear()
        await message.answer(t("reply_failed", lang), reply_markup=get_main_menu_keyboard(lang))
