"""
Finite State Machine (FSM) states for handling conversation flows.
"""
from aiogram.fsm.state import State, StatesGroup


class ListingStates(StatesGroup):
    """Состояния создания и редактирования объявлений."""
    # Создание нового объявления
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_category = State()
    waiting_for_condition = State()
    waiting_for_photos = State()
    waiting_for_location = State()
    confirm_listing = State()

    # Редактирование существующего объявления
    editing_select_field = State()
    editing_title = State()
    editing_description = State()
    editing_price = State()
    editing_category = State()
    editing_condition = State()
    editing_photos = State()


class SearchStates(StatesGroup):
    """Состояния поиска и фильтрации."""
    waiting_for_query = State()
    waiting_for_category = State()
    waiting_for_price_range = State()
    waiting_for_min_price = State()
    waiting_for_max_price = State()
    waiting_for_seller = State()
    waiting_for_location = State()
    browsing_results = State()


class MessageStates(StatesGroup):
    """Состояния общения покупателя и продавца."""
    waiting_for_message = State()
    waiting_for_reply = State()


class ProfileStates(StatesGroup):
    """Состояния редактирования профиля."""
    editing_phone = State()
    editing_location = State()
    editing_bio = State()


class ReviewStates(StatesGroup):
    """Состояния создания отзывов о продавце."""
    waiting_for_rating = State()
    waiting_for_comment = State()


class ReportStates(StatesGroup):
    """Состояния отправки жалоб."""
    waiting_for_comment = State()


class AdminStates(StatesGroup):
    """Состояния админских операций."""
    # Управление пользователями
    blocking_user = State()
    warning_user = State()
    editing_user_profile = State()

    # Управление объявлениями
    flagging_listing = State()
    editing_listing = State()
    deleting_listing = State()

    # Фильтрация аналитики
    filtering_analytics = State()
