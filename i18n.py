"""
Модуль интернационализации (i18n) для Telegram Marketplace Bot.
Поддерживает русский язык по умолчанию и дополнительный английский интерфейс.
"""
from typing import Optional

STRINGS = {
    "ru": {
        # ── Конфигурация / MESSAGES ─────────────────────────────────────────────
        "welcome": """
🛍️ <b>Добро пожаловать в {bot_name}!</b>

Ваш универсальный маркетплейс для покупки и продажи товаров и услуг.

<b>Что вы можете делать:</b>
• 🔍 Просматривать и искать объявления
• ➕ Создавать свои объявления
• 💬 Общаться с покупателями/продавцами
• ❤️ Сохранять в избранное

Используйте кнопки ниже, чтобы начать!
""",
        "help": """
📖 <b>Помощь и команды</b>

<b>Навигация:</b>
• /start - Главное меню
• /search - Поиск объявлений
• /mylistings - Ваши объявления
• /favorites - Избранное
• /profile - Ваш профиль
• /cancel - Отменить операцию

<b>Язык:</b>
• /english - Переключить на английский
• /russian - Переключить на русский

<b>Создание объявления:</b>
1. Перейдите в "Мои объявления" → "Добавить"
2. Введите название, описание, цену
3. Выберите категорию
4. Добавьте фото (по желанию)
5. Подтвердите и опубликуйте!

<b>Покупка:</b>
1. Просматривайте или ищите объявления
2. Смотрите подробности
3. Свяжитесь с продавцом
4. Договоритесь об оплате/доставке

Нужна помощь? Напишите {support}
""",
        "listing_created": "✅ Ваше объявление опубликовано!",
        "listing_updated": "✅ Объявление успешно обновлено!",
        "listing_deleted": "🗑️ Объявление удалено.",
        "no_listings": "📭 Объявления не найдены.",
        "contact_seller_toast": "💬 Сообщение отправлено продавцу!",
        "added_to_favorites": "❤️ Добавлено в избранное!",
        "removed_from_favorites": "💔 Удалено из избранного.",
        "operation_cancelled": "❌ Операция отменена.",

        # ── Команды языка ──────────────────────────────────────────────
        "language_set_en": "🇬🇧 Language switched to English.",
        "language_set_ru": "🇷🇺 Язык переключён на русский.",
        "language_already_en": "🇬🇧 Language is already English.",
        "language_already_ru": "🇷🇺 Язык уже русский.",
        "nothing_to_cancel": "Нечего отменять. Используйте /start для перехода в главное меню.",

        # ── Кнопки клавиатур ───────────────────────────────────────────────
        "btn_browse": "🔍 Обзор объявлений",
        "btn_search": "🔎 Поиск",
        "btn_my_listings": "📝 Мои объявления",
        "btn_favorites": "❤️ Избранное",
        "btn_add_listing": "➕ Добавить объявление",
        "btn_my_profile": "👤 Мой профиль",
        "btn_help": "❓ Помощь",
        "btn_all_categories": "📋 Все категории",
        "btn_back": "◀️ Назад",
        "btn_back_to_menu": "◀️ В главное меню",
        "btn_menu": "◀️ Меню",
        "btn_edit": "✏️ Редактировать",
        "btn_delete": "🗑️ Удалить",
        "btn_mark_sold": "✅ Отметить как продано",
        "btn_contact_seller": "💬 Связаться с продавцом",
        "btn_add_to_favorites": "❤️ В избранное",
        "btn_remove_from_favorites": "💔 Удалить из избранного",
        "btn_leave_review": "⭐ Оставить отзыв",
        "btn_seller_reviews": "📝 Отзывы о продавце",
        "btn_report_listing": "🚩 Пожаловаться на объявление",
        "btn_report_user": "🚩 Пожаловаться на продавца",
        "btn_report_reason_spam": "📢 Спам",
        "btn_report_reason_fraud": "💸 Мошенничество",
        "btn_report_reason_inappropriate": "🔞 Неприемлемый контент",
        "btn_report_reason_wrong_category": "📁 Неверная категория",
        "btn_report_reason_scam": "⚠️ Обман / Скам",
        "btn_report_reason_abuse": "🤬 Оскорбления",
        "btn_report_reason_other": "❓ Другое",
        "btn_skip_report_comment": "⏭️ Пропустить",
        "btn_seller_listings": "🛍️ Все объявления продавца",
        "btn_active_listings": "📋 Активные объявления",
        "btn_sold_listings": "✅ Проданные товары",
        "btn_confirm": "✅ Подтвердить",
        "btn_cancel": "❌ Отмена",
        "btn_skip": "⏭️ Пропустить",
        "btn_done": "✅ Готово",
        "btn_prev": "◀️ Пред.",
        "btn_next": "След. ▶️",
        "btn_reply_to_buyer": "💬 Ответить покупателю",
        "btn_reply_to_seller": "💬 Написать продавцу снова",
        "btn_edit_title": "📝 Название",
        "btn_edit_description": "📄 Описание",
        "btn_edit_price": "💰 Цена",
        "btn_edit_category": "📁 Категория",
        "btn_edit_condition": "📦 Состояние",
        "btn_edit_photos": "📷 Фото",
        "btn_condition_new": "✨ Новый",
        "btn_condition_used": "📦 Б/у",
        "btn_condition_good": "👍 Хорошее",
        "btn_share_contact": "📱 Поделиться контактом",
        "btn_share_location": "📍 Поделиться локацией",
        "btn_my_reviews": "⭐ Мои отзывы",
        "btn_edit_location": "📍 Изменить местоположение",
        "btn_edit_bio": "📝 Изменить о себе",
        "btn_new_search": "🔍 Новый поиск",
        "btn_delete_my_review": "🗑 Удалить мой отзыв",
        "btn_search_keywords": "🔤 Поиск по ключевым словам",
        "btn_search_categories": "📁 Обзор по категориям",
        "btn_search_price": "💰 Фильтр по цене",
        "btn_search_seller": "👤 Поиск по продавцу",
        "btn_search_location": "📍 Поиск по городу",

        # Диапазоны цен
        "price_range_0_25": "До 25 ₽",
        "price_range_25_50": "25 ₽ - 50 ₽",
        "price_range_50_100": "50 ₽ - 100 ₽",
        "price_range_100_500": "100 ₽ - 500 ₽",
        "price_range_500plus": "500 ₽+",
        "price_range_custom": "Свой диапазон",

        # ── Обработчики объявлений ──────────────────────────────────────────────
        "my_listings_menu": "📝 <b>Мои объявления</b>\n\nУправляйте своими объявлениями здесь:",
        "no_active_listings": "📭 У вас пока нет активных объявлений.\n\nНажмите 'Добавить объявление', чтобы создать!",
        "active_listings_header": "📋 <b>Ваши активные объявления</b> ({count})\n\nВыберите объявление для просмотра или редактирования:",
        "no_sold_listings": "📭 У вас пока нет проданных товаров.",
        "sold_listings_header": "✅ <b>Ваши проданные товары</b> ({count})",
        "access_restricted": (
            "🚫 <b>Доступ ограничен</b>\n\n"
            "Ваш аккаунт заблокирован, вы не можете создавать объявления.\n\n"
            "{reason}{until}"
        ),
        "account_blocked_toast": "Ваш аккаунт заблокирован",
        "suspension_reason_prefix": "<b>Причина:</b> {reason}\n",
        "suspension_until_prefix": "<b>Блокировка до:</b> {until}",
        "listing_title_step": (
            "➕ <b>Создание объявления</b>\n\n"
            "Шаг 1/6: Введите <b>название</b> вашего объявления:\n\n"
            "<i>Пример: iPhone 14 Pro Max 256GB</i>"
        ),
        "error_invalid_title": "❌ {error}\n\nПожалуйста, введите корректное название:",
        "listing_description_step": (
            "Шаг 2/6: Введите <b>описание</b> вашего объявления:\n\n"
            "<i>Опишите товар подробно - состояние, характеристики и т.д.</i>"
        ),
        "error_description_too_long": "❌ {error}\n\nПожалуйста, введите более короткое описание:",
        "listing_price_step": (
            "Шаг 3/6: Введите <b>цену</b> вашего объявления:\n\n"
            "<i>Пример: 999.99</i>"
        ),
        "error_invalid_price": "❌ {error}\n\nПожалуйста, введите корректную цену:",
        "listing_category_step": "Шаг 4/6: Выберите <b>категорию</b> для вашего объявления:",
        "listing_condition_step": "Шаг 5/6: Выберите <b>состояние</b> товара:",
        "listing_photos_step": (
            "Шаг 6/6: Отправьте <b>фото</b> вашего товара (до {max_photos}):\n\n"
            "<i>Отправляйте фото по одному, затем нажмите 'Готово'.</i>\n"
            "<i>Вы также можете пропустить этот шаг.</i>"
        ),
        "photos_max_reached": "❌ Максимум {max_photos} фото. Нажмите 'Готово' для продолжения.",
        "photo_added": (
            "✅ Фото добавлено! ({current}/{max})\n\n"
            "Отправьте ещё фото или нажмите 'Готово' для продолжения."
        ),
        "photos_remaining": " (осталось {remaining})",
        "listing_confirm_header": "📋 <b>Подтверждение объявления</b>\n\n",
        "listing_confirm_title": "<b>Название:</b> {title}\n",
        "listing_confirm_price": "<b>Цена:</b> {price}\n",
        "listing_confirm_category": "<b>Категория:</b> {category_name}\n",
        "listing_confirm_condition": "<b>Состояние:</b> {condition}\n",
        "listing_confirm_photos": "<b>Фото:</b> {count}\n",
        "listing_confirm_description": "<b>Описание:</b> {desc}\n",
        "listing_confirm_question": "\nВсё верно?",
        "listing_published_text": (
            "✅ <b>Объявление опубликовано!</b>\n\n"
            "Ваше объявление \"{title}\" теперь активно.\n\n"
            "Покупатели теперь могут найти и связаться с вами по этому товару."
        ),
        "listing_not_found": "Объявление не найдено.",
        "select_action": "Выберите действие:",
        "recent_listings_header": "🛍️ <b>Последние объявления</b>\n\nВыберите объявление для просмотра:",
        "edit_listing_menu": (
            "✏️ <b>Редактирование объявления</b>\n\n"
            "<b>{title}</b>\n\n"
            "Выберите, что хотите изменить:"
        ),
        "cannot_edit_others": "Вы можете редактировать только свои объявления.",
        "edit_title_prompt": "Текущее название: <b>{current}</b>\n\nВведите новое название:",
        "edit_description_prompt": "Текущее описание: {current}\n\nВведите новое описание:",
        "edit_price_prompt": "Текущая цена: {current}\n\nВведите новую цену:",
        "edit_category_prompt": "Текущая категория: {current}\n\nВыберите новую категорию:",
        "edit_photos_info": (
            "📷 <b>Управление фото</b>\n\n"
            "Чтобы обновить фото, удалите объявление и создайте новое.\n\n"
            "<i>Полное управление фото будет в будущем обновлении!</i>"
        ),
        "delete_confirm": (
            "🗑️ <b>Удалить объявление?</b>\n\n"
            "Вы уверены, что хотите удалить:\n"
            "<b>{title}</b>\n\n"
            "Это действие нельзя отменить."
        ),
        "cannot_delete_others": "Вы можете удалять только свои объявления.",
        "mark_sold_success": (
            "✅ <b>Отмечено как продано!</b>\n\n"
            "<b>{title}</b> отмечено как проданное.\n\n"
            "Поздравляем с продажей! 🎉"
        ),
        "mark_sold_toast": "Объявление отмечено как продано!",
        "cannot_change_others": "Вы можете изменять только свои объявления.",
        "favorites_empty": (
            "❤️ <b>Ваше избранное</b>\n\n"
            "Вы пока не сохранили ни одного объявления.\n\n"
            "Просматривайте объявления и нажимайте ❤️, чтобы сохранить их здесь!"
        ),
        "favorites_header": "❤️ <b>Ваше избранное</b> ({count})",
        "no_description": "Нет описания",
        "status_sold": "Продано",

        # ── Обработчики поиска ────────────────────────────────────────────────
        "search_menu": "🔍 <b>Поиск объявлений</b>\n\nКак вы хотите искать?",
        "search_keywords_prompt": (
            "🔤 <b>Поиск по ключевым словам</b>\n\n"
            "Введите ключевые слова для поиска:\n\n"
            "<i>Пример: iPhone, кожаная куртка, велосипед</i>"
        ),
        "search_query_too_short": "❌ Поисковый запрос слишком короткий. Введите минимум 2 символа.",
        "search_categories_header": "📁 <b>Обзор по категориям</b>\n\nВыберите категорию:",
        "search_price_header": "💰 <b>Фильтр по цене</b>\n\nВыберите диапазон цен:",
        "search_price_custom_min": (
            "💰 <b>Свой диапазон цен</b>\n\n"
            "Введите <b>минимальную</b> цену (или 0, если без минимума):"
        ),
        "search_price_custom_max": (
            "💰 <b>Свой диапазон цен</b>\n\n"
            "Введите <b>максимальную</b> цену (или 0, если без максимума):"
        ),
        "error_invalid_min_price": "❌ {error}\n\nПожалуйста, введите корректную минимальную цену:",
        "error_invalid_max_price": "❌ {error}\n\nПожалуйста, введите корректную максимальную цену:",
        "search_seller_prompt": (
            "👤 <b>Поиск по продавцу</b>\n\n"
            "Введите имя пользователя (с @ или без) или имя продавца:\n\n"
            "<i>Пример: @username, username, или Иван Петров</i>"
        ),
        "search_seller_not_found": (
            "❌ Продавец \"{seller}\" не найден.\n\n"
            "Попробуйте другое имя пользователя или имя."
        ),
        "search_location_prompt": (
            "📍 <b>Поиск по городу</b>\n\n"
            "Введите название города или района:\n\n"
            "<i>Пример: Москва, Санкт-Петербург, ЦАО</i>"
        ),
        "search_no_results": "\n<i>Попробуйте другие фильтры или поисковые запросы.</i>",
        "search_select_listing": "\n<i>Выберите объявление для просмотра:</i>",

        # ── Заголовок результатов поиска (helpers) ───────────────────────────────
        "search_results_header": "🔍 <b>Результаты поиска</b>\n\n",
        "search_filters_label": "Фильтры: {filters}\n\n",
        "search_keywords_filter": "Ключевые слова: \"{query}\"",
        "search_category_filter": "Категория: {category}",
        "search_seller_filter": "Продавец: {seller}",
        "search_location_filter": "Город: {location}",
        "search_price_both": "Цена: {min} - {max}",
        "search_price_from": "Цена: от {min}",
        "search_price_to": "Цена: до {max}",
        "search_total_found": "Найдено <b>{total}</b> объявлений\n",

        # ── Обработчики сообщений ──────────────────────────────────────────────
        "contact_seller_header": (
            "💬 <b>Связаться с продавцом</b>\n\n"
            "Объявление: <b>{title}</b>\n"
            "Продавец: {seller}\n\n"
            "Напишите ваше сообщение продавцу:\n\n"
            "<i>Советы:\n"
            "• Будьте вежливы и понятны\n"
            "• Задайте вопросы о товаре\n"
            "• Укажите, если хотите торговаться</i>"
        ),
        "cannot_message_self": "Вы не можете написать себе!",
        "message_too_short": "❌ Сообщение слишком короткое. Напишите полноценное сообщение:",
        "message_too_long": "❌ Сообщение слишком длинное. Ограничьте его 1000 символами:",
        "listing_not_exists": "❌ Объявление больше не существует.",
        "seller_notification": (
            "📩 <b>Новое сообщение!</b>\n\n"
            "От: {buyer}{username_part}\n\n"
            "По объявлению: <b>{title}</b>\n"
            "Цена: {price}\n\n"
            "<b>Сообщение:</b>\n{text}"
        ),
        "message_sent_success": (
            "✅ <b>Сообщение отправлено!</b>\n\n"
            "Ваше сообщение отправлено продавцу.\n\n"
        ),
        "contact_seller_direct": "Вы также можете связаться с продавцом напрямую: @{username}",
        "seller_will_reply": "Продавец ответит вам через этот бот или Telegram.",
        "message_failed": (
            "❌ <b>Не удалось отправить</b>\n\n"
            "Telegram-аккаунт продавца не смог получить сообщение.\n"
            "Возможно, продавец заблокировал бота.\n\n"
            "Попробуйте позже."
        ),
        "reply_to_buyer_prompt": "💬 <b>Ответ покупателю</b>\n\nНапишите ваш ответ:",
        "reply_too_short": "❌ Сообщение слишком короткое. Напишите полноценный ответ:",
        "buyer_not_found": "❌ Покупатель не найден.",
        "seller_reply_notification": (
            "📩 <b>Ответ продавца!</b>\n\n"
            "От: {seller}{username_part}"
        ),
        "seller_reply_listing_part": "\n\nПо объявлению: <b>{title}</b>",
        "seller_reply_message_part": "\n\n<b>Сообщение:</b>\n{text}",
        "reply_sent": "✅ <b>Ответ отправлен!</b>",
        "reply_failed": "❌ Не удалось отправить ответ. Попробуйте позже.",

        # ── Жалобы ───────────────────────────────────────────────────────
        "report_listing_header": (
            "🚩 <b>Пожаловаться на объявление</b>\n\n"
            "<b>{title}</b>\n\n"
            "Выберите причину жалобы:"
        ),
        "report_user_header": (
            "🚩 <b>Пожаловаться на продавца</b>\n\n"
            "<b>{name}</b>\n\n"
            "Выберите причину жалобы:"
        ),
        "report_comment_prompt": (
            "💬 <b>Дополнительные сведения</b> (необязательно)\n\n"
            "Опишите подробнее, что случилось, или нажмите «Пропустить»:"
        ),
        "report_already_sent": "⚠️ Вы уже подавали жалобу на это.",
        "report_cannot_report_self": "⚠️ Нельзя жаловаться на самого себя.",
        "report_success": (
            "✅ <b>Жалоба принята!</b>\n\n"
            "Спасибо — наши модераторы рассмотрят её в ближайшее время."
        ),
        "report_admin_notify_listing": (
            "🚨 <b>Новая жалоба на объявление #{listing_id}</b>\n\n"
            "Объявление: <b>{title}</b>\n"
            "От: {reporter}\n"
            "Причина: {reason}\n"
            "{comment_line}"
            "Всего жалоб: {count}"
        ),
        "report_admin_notify_user": (
            "🚨 <b>Новая жалоба на пользователя #{user_id}</b>\n\n"
            "Пользователь: {name}\n"
            "От: {reporter}\n"
            "Причина: {reason}\n"
            "{comment_line}"
            "Всего жалоб: {count}"
        ),
        "report_admin_comment_line": "Комментарий: {comment}\n",
        "report_auto_flagged": "\n🚩 <b>Объявление автоматически отмечено</b> (достигнут порог жалоб).",
        "report_reason_spam": "Спам",
        "report_reason_fraud": "Мошенничество",
        "report_reason_inappropriate": "Неприемлемый контент",
        "report_reason_wrong_category": "Неверная категория",
        "report_reason_scam": "Обман / Скам",
        "report_reason_abuse": "Оскорбления",
        "report_reason_other": "Другое",

        # ── Обработчики профиля ───────────────────────────────────────────────
        "profile_stats": "\n📊 <b>Статистика:</b>\n• Активных объявлений: {active}\n• Продано товаров: {sold}\n",
        "edit_location_prompt": (
            "📍 <b>Изменить местоположение</b>\n\n"
            "Текущее: {current}\n\n"
            "Введите ваше новое местоположение:\n\n"
            "<i>Пример: Москва или Санкт-Петербург</i>"
        ),
        "location_too_long": "❌ Местоположение слишком длинное. Ограничьте его 100 символами:",
        "location_updated": "✅ <b>Местоположение обновлено!</b>\n\nВаше местоположение: {location}",
        "edit_bio_prompt": (
            "📝 <b>Изменить информацию о себе</b>\n\n"
            "Текущая: {current}\n\n"
            "Напишите что-нибудь о себе:\n\n"
            "<i>Это поможет покупателям больше вам доверять!</i>"
        ),
        "bio_too_long": "❌ Информация слишком длинная. Ограничьте её 500 символами:",
        "bio_updated": "✅ <b>Информация о себе обновлена!</b>\n\nВаша информация: {bio}",
        "not_specified": "Не указано",
        "payment_settings": (
            "💳 <b>Настройки оплаты</b>\n\n"
            "Интеграция оплаты скоро появится!\n\n"
            "<i>Эта функция позволит вам:\n"
            "• Привязать способы оплаты\n"
            "• Получать безопасные платежи\n"
            "• Отслеживать историю транзакций</i>"
        ),
        "verification": (
            "✅ <b>Верификация</b>\n\n"
            "Верификация продавцов скоро появится!\n\n"
            "<i>Преимущества верификации:\n"
            "• Значок верификации на ваших объявлениях\n"
            "• Повышенное доверие покупателей\n"
            "• Приоритет в результатах поиска</i>"
        ),

        # ── Обработчики отзывов ───────────────────────────────────────────────
        "review_prompt": (
            "⭐ <b>Отзыв о продавце {seller}</b>\n\n"
            "Объявление: <b>{title}</b>\n\n"
            "Выберите оценку от 1 до 5 звёзд:"
        ),
        "cannot_review_self": "Вы не можете оставить отзыв о себе.",
        "already_reviewed": "Вы уже оставили отзыв на это объявление.",
        "rate_comment_prompt": "Ваша оценка: {stars} ({rating}/5)\n\nНапишите комментарий к отзыву или нажмите «Пропустить»:",
        "comment_too_long": "❌ Комментарий слишком длинный. Ограничьте его 500 символами:",
        "review_saved": "✅ <b>Отзыв сохранён!</b>\n\nОценка: {stars}\n",
        "review_with_comment": "Комментарий: {comment}",
        "review_failed": "❌ Не удалось сохранить отзыв. Возможно, вы уже оставляли отзыв на это объявление.",
        "seller_reviews_header": (
            "⭐ <b>Отзывы о {seller}</b>\n"
            "Средний рейтинг: {stars} {rating:.1f} ({total} отзывов)\n\n"
        ),
        "no_reviews": "⭐ <b>Отзывы о {seller}</b>\n\nПока нет отзывов.",
        "seller_listings_header": "🛍️ <b>Объявления продавца {seller}</b> ({count})\n\nВыберите объявление:",
        "seller_no_listings": "🛍️ <b>Объявления продавца {seller}</b>\n\nУ этого продавца пока нет активных объявлений.",
        "seller_not_found": "Продавец не найден.",
        "delete_review_confirm": (
            "🗑 <b>Удаление отзыва</b>\n\n"
            "Оценка: {stars}\n"
        ),
        "delete_review_comment_line": "Комментарий: {comment}\n",
        "delete_review_question": "\nВы уверены, что хотите удалить этот отзыв?",
        "review_not_found": "Отзыв не найден.",
        "cannot_delete_others_review": "Вы можете удалять только свои отзывы.",
        "review_deleted": "✅ Отзыв успешно удалён.",
        "review_delete_failed": "❌ Не удалось удалить отзыв. Попробуйте позже.",
        "new_review_notification": (
            "📬 <b>Новый отзыв!</b>\n\n"
            "Пользователь <b>{reviewer}</b> оставил отзыв "
            "на ваше объявление «{listing}».\n\n"
            "Оценка: {stars} ({rating}/5)"
        ),
        "new_review_comment": "\nКомментарий: {comment}",
        "listing_title_fallback": "объявление",

        "edit_condition_prompt": "Текущее состояние: {current}\n\nВыберите новое состояние:",
        "condition_new": "✨ Новый",
        "condition_used": "📦 Б/у",
        "condition_good": "👍 Хорошее состояние",

        # ── Утилиты / format_listing_text ─────────────────────────────────
        "listing_price_label": "💰 <b>Цена:</b> {price}",
        "listing_category_label": "📁 <b>Категория:</b> {category}",
        "listing_condition_label": "📦 <b>Состояние:</b> {condition}",
        "listing_location_label": "📍 <b>Местоположение:</b> {location}",
        "listing_description_label": "📝 <b>Описание:</b>\n{description}",
        "listing_seller_label": "\n👤 <b>Продавец:</b> {name}",
        "listing_seller_rating": " ⭐ {rating:.1f} ({count} отзывов)",
        "listing_views_label": "\n\n👁️ Просмотров: {views}",
        "listing_status_label": "\n{emoji} Статус: {status}",
        "status_sold_text": "Продано",

        # ── Утилиты / format_user_profile ─────────────────────────────────
        "profile_header_text": "👤 <b>Ваш профиль</b>\n\n",
        "profile_name_label": "<b>Имя:</b> {name}\n",
        "profile_username_label": "<b>Имя пользователя:</b> @{username}\n",
        "profile_phone_label": "<b>Телефон:</b> {phone}\n",
        "profile_location_label": "<b>Местоположение:</b> {location}\n",
        "profile_bio_label": "<b>О себе:</b> {bio}\n",
        "profile_rating_label": "\n⭐ <b>Рейтинг:</b> {rating:.1f} ({count} отзывов)\n",
        "profile_verified": "✅ Верифицированный продавец\n",

        # ── Утилиты / format_review_text ──────────────────────────────────
        "reviewer_unknown": "Пользователь #{id}",

        # ── Утилиты / validate_* ──────────────────────────────────────────
        "validate_price_negative": "Цена не может быть отрицательной.",
        "validate_price_too_high": "Цена не может превышать 1 000 000 ₽.",
        "validate_price_invalid": "Пожалуйста, введите корректное число для цены.",
        "validate_title_empty": "Название не может быть пустым.",
        "validate_title_too_short": "Название должно быть не менее 3 символов.",
        "validate_title_too_long": "Название не может превышать 100 символов.",
        "validate_description_too_long": "Описание не может превышать 2000 символов.",

        # ── Категории ────────────────────────────────────────────────────
        "cat_electronics": "📱 Электроника",
        "cat_clothing": "👕 Одежда и мода",
        "cat_home": "🏠 Дом и сад",
        "cat_vehicles": "🚗 Транспорт",
        "cat_services": "🔧 Услуги",
        "cat_jobs": "💼 Работа",
        "cat_pets": "🐾 Животные",
        "cat_sports": "⚽ Спорт и хобби",
        "cat_books": "📚 Книги и обучение",
        "cat_other": "📦 Другое",
    },

    "en": {
        # ── Конфигурация / MESSAGES ─────────────────────────────────────────────
        "welcome": """
🛍️ <b>Welcome to {bot_name}!</b>

Your all-in-one marketplace for buying and selling goods and services.

<b>What you can do:</b>
• 🔍 Browse and search listings
• ➕ Create your own listings
• 💬 Chat with buyers/sellers
• ❤️ Save to favorites

Use the buttons below to get started!
""",
        "help": """
📖 <b>Help & Commands</b>

<b>Navigation:</b>
• /start - Main menu
• /search - Search listings
• /mylistings - Your listings
• /favorites - Saved listings
• /profile - Your profile
• /cancel - Cancel operation

<b>Language:</b>
• /english - Switch to English
• /russian - Switch to Russian

<b>Creating a listing:</b>
1. Go to "My Listings" → "Add"
2. Enter title, description, price
3. Choose a category
4. Add photos (optional)
5. Confirm and publish!

<b>Buying:</b>
1. Browse or search listings
2. View details
3. Contact the seller
4. Agree on payment/delivery

Need help? Write to {support}
""",
        "listing_created": "✅ Your listing has been published!",
        "listing_updated": "✅ Listing updated successfully!",
        "listing_deleted": "🗑️ Listing deleted.",
        "no_listings": "📭 No listings found.",
        "contact_seller_toast": "💬 Message sent to seller!",
        "added_to_favorites": "❤️ Added to favorites!",
        "removed_from_favorites": "💔 Removed from favorites.",
        "operation_cancelled": "❌ Operation cancelled.",

        # ── Команды языка ──────────────────────────────────────────────
        "language_set_en": "🇬🇧 Language switched to English.",
        "language_set_ru": "🇷🇺 Language switched to Russian.",
        "language_already_en": "🇬🇧 Language is already English.",
        "language_already_ru": "🇷🇺 Language is already Russian.",
        "nothing_to_cancel": "Nothing to cancel. Use /start to go to the main menu.",

        # ── Кнопки клавиатур ───────────────────────────────────────────────
        "btn_browse": "🔍 Browse Listings",
        "btn_search": "🔎 Search",
        "btn_my_listings": "📝 My Listings",
        "btn_favorites": "❤️ Favorites",
        "btn_add_listing": "➕ Add Listing",
        "btn_my_profile": "👤 My Profile",
        "btn_help": "❓ Help",
        "btn_all_categories": "📋 All Категории",
        "btn_back": "◀️ Back",
        "btn_back_to_menu": "◀️ Main Menu",
        "btn_menu": "◀️ Menu",
        "btn_edit": "✏️ Edit",
        "btn_delete": "🗑️ Delete",
        "btn_mark_sold": "✅ Mark as Sold",
        "btn_contact_seller": "💬 Contact Seller",
        "btn_add_to_favorites": "❤️ Add to Favorites",
        "btn_remove_from_favorites": "💔 Remove from Favorites",
        "btn_leave_review": "⭐ Leave a Review",
        "btn_report_listing": "🚩 Report Listing",
        "btn_report_user": "🚩 Report Seller",
        "btn_report_reason_spam": "📢 Spam",
        "btn_report_reason_fraud": "💸 Fraud",
        "btn_report_reason_inappropriate": "🔞 Inappropriate Content",
        "btn_report_reason_wrong_category": "📁 Wrong Category",
        "btn_report_reason_scam": "⚠️ Scam",
        "btn_report_reason_abuse": "🤬 Abuse",
        "btn_report_reason_other": "❓ Other",
        "btn_skip_report_comment": "⏭️ Skip",
        "btn_seller_reviews": "📝 Seller Reviews",
        "btn_seller_listings": "🛍️ All Seller Listings",
        "btn_active_listings": "📋 Active Listings",
        "btn_sold_listings": "✅ Sold Items",
        "btn_confirm": "✅ Confirm",
        "btn_cancel": "❌ Cancel",
        "btn_skip": "⏭️ Skip",
        "btn_done": "✅ Done",
        "btn_prev": "◀️ Prev",
        "btn_next": "Next ▶️",
        "btn_reply_to_buyer": "💬 Reply to Buyer",
        "btn_reply_to_seller": "💬 Message Seller Again",
        "btn_edit_title": "📝 Title",
        "btn_edit_description": "📄 Description",
        "btn_edit_price": "💰 Price",
        "btn_edit_category": "📁 Category",
        "btn_edit_condition": "📦 Condition",
        "btn_edit_photos": "📷 Photos",
        "btn_condition_new": "✨ New",
        "btn_condition_used": "📦 Used",
        "btn_condition_good": "👍 Good",
        "btn_share_contact": "📱 Share Contact",
        "btn_share_location": "📍 Share Location",
        "btn_my_reviews": "⭐ My Reviews",
        "btn_edit_location": "📍 Change Location",
        "btn_edit_bio": "📝 Edit About Me",
        "btn_new_search": "🔍 New Search",
        "btn_delete_my_review": "🗑 Delete My Review",
        "btn_search_keywords": "🔤 Search by Keywords",
        "btn_search_categories": "📁 Browse by Category",
        "btn_search_price": "💰 Filter by Price",
        "btn_search_seller": "👤 Search by Seller",
        "btn_search_location": "📍 Search by City",

        # Диапазоны цен
        "price_range_0_25": "Under 25 ₽",
        "price_range_25_50": "25 ₽ - 50 ₽",
        "price_range_50_100": "50 ₽ - 100 ₽",
        "price_range_100_500": "100 ₽ - 500 ₽",
        "price_range_500plus": "500 ₽+",
        "price_range_custom": "Custom Range",

        # ── Обработчики объявлений ──────────────────────────────────────────────
        "my_listings_menu": "📝 <b>My Listings</b>\n\nManage your listings here:",
        "no_active_listings": "📭 You have no active listings yet.\n\nClick 'Add Listing' to create one!",
        "active_listings_header": "📋 <b>Your Active Listings</b> ({count})\n\nSelect a listing to view or edit:",
        "no_sold_listings": "📭 You have no sold items yet.",
        "sold_listings_header": "✅ <b>Your Sold Items</b> ({count})",
        "access_restricted": (
            "🚫 <b>Access Restricted</b>\n\n"
            "Your account is blocked, you cannot create listings.\n\n"
            "{reason}{until}"
        ),
        "account_blocked_toast": "Your account is blocked",
        "suspension_reason_prefix": "<b>Reason:</b> {reason}\n",
        "suspension_until_prefix": "<b>Blocked until:</b> {until}",
        "listing_title_step": (
            "➕ <b>Create Listing</b>\n\n"
            "Step 1/6: Enter the <b>title</b> of your listing:\n\n"
            "<i>Example: iPhone 14 Pro Max 256GB</i>"
        ),
        "error_invalid_title": "❌ {error}\n\nPlease enter a valid title:",
        "listing_description_step": (
            "Step 2/6: Enter the <b>description</b> of your listing:\n\n"
            "<i>Describe the item in detail — condition, specs, etc.</i>"
        ),
        "error_description_too_long": "❌ {error}\n\nPlease enter a shorter description:",
        "listing_price_step": (
            "Step 3/6: Enter the <b>price</b> of your listing:\n\n"
            "<i>Example: 999.99</i>"
        ),
        "error_invalid_price": "❌ {error}\n\nPlease enter a valid price:",
        "listing_category_step": "Step 4/6: Choose a <b>category</b> for your listing:",
        "listing_condition_step": "Step 5/6: Select the <b>condition</b> of the item:",
        "listing_photos_step": (
            "Step 6/6: Send <b>photos</b> of your item (up to {max_photos}):\n\n"
            "<i>Send photos one by one, then press 'Done'.</i>\n"
            "<i>You can also skip this step.</i>"
        ),
        "photos_max_reached": "❌ Maximum {max_photos} photos. Press 'Done' to continue.",
        "photo_added": (
            "✅ Photo added! ({current}/{max})\n\n"
            "Send more photos or press 'Done' to continue."
        ),
        "photos_remaining": " ({remaining} left)",
        "listing_confirm_header": "📋 <b>Confirm Listing</b>\n\n",
        "listing_confirm_title": "<b>Title:</b> {title}\n",
        "listing_confirm_price": "<b>Price:</b> {price}\n",
        "listing_confirm_category": "<b>Category:</b> {category_name}\n",
        "listing_confirm_condition": "<b>Condition:</b> {condition}\n",
        "listing_confirm_photos": "<b>Photos:</b> {count}\n",
        "listing_confirm_description": "<b>Description:</b> {desc}\n",
        "listing_confirm_question": "\nEverything correct?",
        "listing_published_text": (
            "✅ <b>Listing Published!</b>\n\n"
            "Your listing \"{title}\" is now active.\n\n"
            "Buyers can now find and contact you about this item."
        ),
        "listing_not_found": "Listing not found.",
        "select_action": "Choose an action:",
        "recent_listings_header": "🛍️ <b>Recent Listings</b>\n\nSelect a listing to view:",
        "edit_listing_menu": (
            "✏️ <b>Edit Listing</b>\n\n"
            "<b>{title}</b>\n\n"
            "Select what you want to change:"
        ),
        "cannot_edit_others": "You can only edit your own listings.",
        "edit_title_prompt": "Current title: <b>{current}</b>\n\nEnter new title:",
        "edit_description_prompt": "Current description: {current}\n\nEnter new description:",
        "edit_price_prompt": "Current price: {current}\n\nEnter new price:",
        "edit_category_prompt": "Current category: {current}\n\nChoose new category:",
        "edit_photos_info": (
            "📷 <b>Photo Management</b>\n\n"
            "To update photos, delete the listing and create a new one.\n\n"
            "<i>Full photo management coming in a future update!</i>"
        ),
        "delete_confirm": (
            "🗑️ <b>Delete Listing?</b>\n\n"
            "Are you sure you want to delete:\n"
            "<b>{title}</b>\n\n"
            "This action cannot be undone."
        ),
        "cannot_delete_others": "You can only delete your own listings.",
        "mark_sold_success": (
            "✅ <b>Marked as Sold!</b>\n\n"
            "<b>{title}</b> has been marked as sold.\n\n"
            "Congratulations on your sale! 🎉"
        ),
        "mark_sold_toast": "Listing marked as sold!",
        "cannot_change_others": "You can only change your own listings.",
        "favorites_empty": (
            "❤️ <b>Your Favorites</b>\n\n"
            "You haven't saved any listings yet.\n\n"
            "Browse listings and tap ❤️ to save them here!"
        ),
        "favorites_header": "❤️ <b>Your Favorites</b> ({count})",
        "no_description": "No description",
        "status_sold": "Sold",

        # ── Обработчики поиска ────────────────────────────────────────────────
        "search_menu": "🔍 <b>Search Listings</b>\n\nHow would you like to search?",
        "search_keywords_prompt": (
            "🔤 <b>Search by Keywords</b>\n\n"
            "Enter keywords to search:\n\n"
            "<i>Example: iPhone, leather jacket, bicycle</i>"
        ),
        "search_query_too_short": "❌ Search query too short. Enter at least 2 characters.",
        "search_categories_header": "📁 <b>Browse by Category</b>\n\nSelect a category:",
        "search_price_header": "💰 <b>Filter by Price</b>\n\nSelect a price range:",
        "search_price_custom_min": (
            "💰 <b>Custom Price Range</b>\n\n"
            "Enter the <b>minimum</b> price (or 0 for no minimum):"
        ),
        "search_price_custom_max": (
            "💰 <b>Custom Price Range</b>\n\n"
            "Enter the <b>maximum</b> price (or 0 for no maximum):"
        ),
        "error_invalid_min_price": "❌ {error}\n\nPlease enter a valid minimum price:",
        "error_invalid_max_price": "❌ {error}\n\nPlease enter a valid maximum price:",
        "search_seller_prompt": (
            "👤 <b>Search by Seller</b>\n\n"
            "Enter username (with or without @) or seller's name:\n\n"
            "<i>Example: @username, username, or John Smith</i>"
        ),
        "search_seller_not_found": (
            "❌ Seller \"{seller}\" not found.\n\n"
            "Try a different username or name."
        ),
        "search_location_prompt": (
            "📍 <b>Search by City</b>\n\n"
            "Enter a city or district name:\n\n"
            "<i>Example: Moscow, Saint Petersburg, Downtown</i>"
        ),
        "search_no_results": "\n<i>Try different filters or search terms.</i>",
        "search_select_listing": "\n<i>Select a listing to view:</i>",

        # ── Заголовок результатов поиска (helpers) ───────────────────────────────
        "search_results_header": "🔍 <b>Search Results</b>\n\n",
        "search_filters_label": "Filters: {filters}\n\n",
        "search_keywords_filter": "Keywords: \"{query}\"",
        "search_category_filter": "Category: {category}",
        "search_seller_filter": "Seller: {seller}",
        "search_location_filter": "City: {location}",
        "search_price_both": "Price: {min} - {max}",
        "search_price_from": "Price: from {min}",
        "search_price_to": "Price: up to {max}",
        "search_total_found": "Found <b>{total}</b> listings\n",

        # ── Обработчики сообщений ──────────────────────────────────────────────
        "contact_seller_header": (
            "💬 <b>Contact Seller</b>\n\n"
            "Listing: <b>{title}</b>\n"
            "Seller: {seller}\n\n"
            "Write your message to the seller:\n\n"
            "<i>Tips:\n"
            "• Be polite and clear\n"
            "• Ask questions about the item\n"
            "• Mention if you want to negotiate</i>"
        ),
        "cannot_message_self": "You cannot message yourself!",
        "message_too_short": "❌ Message too short. Write a proper message:",
        "message_too_long": "❌ Message too long. Keep it under 1000 characters:",
        "listing_not_exists": "❌ This listing no longer exists.",
        "seller_notification": (
            "📩 <b>New Message!</b>\n\n"
            "From: {buyer}{username_part}\n\n"
            "About listing: <b>{title}</b>\n"
            "Price: {price}\n\n"
            "<b>Message:</b>\n{text}"
        ),
        "message_sent_success": (
            "✅ <b>Message Sent!</b>\n\n"
            "Your message has been sent to the seller.\n\n"
        ),
        "contact_seller_direct": "You can also contact the seller directly: @{username}",
        "seller_will_reply": "The seller will reply via this bot or Telegram.",
        "message_failed": (
            "❌ <b>Failed to Send</b>\n\n"
            "The seller's Telegram account could not receive your message.\n"
            "They may have blocked the bot.\n\n"
            "Try again later."
        ),
        "reply_to_buyer_prompt": "💬 <b>Reply to Buyer</b>\n\nWrite your reply:",
        "reply_too_short": "❌ Message too short. Write a proper reply:",
        "buyer_not_found": "❌ Buyer not found.",
        "seller_reply_notification": (
            "📩 <b>Seller's Reply!</b>\n\n"
            "From: {seller}{username_part}"
        ),
        "seller_reply_listing_part": "\n\nAbout listing: <b>{title}</b>",
        "seller_reply_message_part": "\n\n<b>Message:</b>\n{text}",
        "reply_sent": "✅ <b>Reply Sent!</b>",
        "reply_failed": "❌ Failed to send reply. Try again later.",

        # ── Жалобы ───────────────────────────────────────────────────────
        "report_listing_header": (
            "🚩 <b>Report Listing</b>\n\n"
            "<b>{title}</b>\n\n"
            "Select the reason for your report:"
        ),
        "report_user_header": (
            "🚩 <b>Report Seller</b>\n\n"
            "<b>{name}</b>\n\n"
            "Select the reason for your report:"
        ),
        "report_comment_prompt": (
            "💬 <b>Additional details</b> (optional)\n\n"
            "Describe what happened in more detail, or press «Skip»:"
        ),
        "report_already_sent": "⚠️ You have already reported this.",
        "report_cannot_report_self": "⚠️ You cannot report yourself.",
        "report_success": (
            "✅ <b>Report submitted!</b>\n\n"
            "Thank you — our moderators will review it shortly."
        ),
        "report_admin_notify_listing": (
            "🚨 <b>New report on listing #{listing_id}</b>\n\n"
            "Listing: <b>{title}</b>\n"
            "From: {reporter}\n"
            "Reason: {reason}\n"
            "{comment_line}"
            "Total reports: {count}"
        ),
        "report_admin_notify_user": (
            "🚨 <b>New report on user #{user_id}</b>\n\n"
            "User: {name}\n"
            "From: {reporter}\n"
            "Reason: {reason}\n"
            "{comment_line}"
            "Total reports: {count}"
        ),
        "report_admin_comment_line": "Comment: {comment}\n",
        "report_auto_flagged": "\n🚩 <b>Listing auto-flagged</b> (report threshold reached).",
        "report_reason_spam": "Spam",
        "report_reason_fraud": "Fraud",
        "report_reason_inappropriate": "Inappropriate Content",
        "report_reason_wrong_category": "Wrong Category",
        "report_reason_scam": "Scam",
        "report_reason_abuse": "Abuse",
        "report_reason_other": "Other",

        # ── Обработчики профиля ───────────────────────────────────────────────
        "profile_stats": "\n📊 <b>Stats:</b>\n• Active listings: {active}\n• Items sold: {sold}\n",
        "edit_location_prompt": (
            "📍 <b>Change Location</b>\n\n"
            "Current: {current}\n\n"
            "Enter your new location:\n\n"
            "<i>Example: New York or London</i>"
        ),
        "location_too_long": "❌ Location too long. Keep it under 100 characters:",
        "location_updated": "✅ <b>Location Updated!</b>\n\nYour location: {location}",
        "edit_bio_prompt": (
            "📝 <b>Edit About Me</b>\n\n"
            "Current: {current}\n\n"
            "Write something about yourself:\n\n"
            "<i>This helps buyers trust you more!</i>"
        ),
        "bio_too_long": "❌ Bio too long. Keep it under 500 characters:",
        "bio_updated": "✅ <b>About Me Updated!</b>\n\nYour info: {bio}",
        "not_specified": "Not specified",
        "payment_settings": (
            "💳 <b>Payment Settings</b>\n\n"
            "Payment integration coming soon!\n\n"
            "<i>This feature will let you:\n"
            "• Link payment methods\n"
            "• Receive secure payments\n"
            "• Track transaction history</i>"
        ),
        "verification": (
            "✅ <b>Verification</b>\n\n"
            "Seller verification coming soon!\n\n"
            "<i>Benefits of verification:\n"
            "• Verification badge on your listings\n"
            "• More buyer trust\n"
            "• Priority in search results</i>"
        ),

        # ── Обработчики отзывов ───────────────────────────────────────────────
        "review_prompt": (
            "⭐ <b>Review for {seller}</b>\n\n"
            "Listing: <b>{title}</b>\n\n"
            "Choose a rating from 1 to 5 stars:"
        ),
        "cannot_review_self": "You cannot leave a review for yourself.",
        "already_reviewed": "You have already reviewed this listing.",
        "rate_comment_prompt": "Your rating: {stars} ({rating}/5)\n\nWrite a comment or press «Skip»:",
        "comment_too_long": "❌ Comment too long. Keep it under 500 characters:",
        "review_saved": "✅ <b>Review Saved!</b>\n\nRating: {stars}\n",
        "review_with_comment": "Comment: {comment}",
        "review_failed": "❌ Failed to save review. You may have already reviewed this listing.",
        "seller_reviews_header": (
            "⭐ <b>Reviews for {seller}</b>\n"
            "Average rating: {stars} {rating:.1f} ({total} reviews)\n\n"
        ),
        "no_reviews": "⭐ <b>Reviews for {seller}</b>\n\nNo reviews yet.",
        "seller_listings_header": "🛍️ <b>Listings by {seller}</b> ({count})\n\nSelect a listing:",
        "seller_no_listings": "🛍️ <b>Listings by {seller}</b>\n\nThis seller has no active listings.",
        "seller_not_found": "Seller not found.",
        "delete_review_confirm": (
            "🗑 <b>Delete Review</b>\n\n"
            "Rating: {stars}\n"
        ),
        "delete_review_comment_line": "Comment: {comment}\n",
        "delete_review_question": "\nAre you sure you want to delete this review?",
        "review_not_found": "Review not found.",
        "cannot_delete_others_review": "You can only delete your own reviews.",
        "review_deleted": "✅ Review deleted successfully.",
        "review_delete_failed": "❌ Failed to delete review. Try again later.",
        "new_review_notification": (
            "📬 <b>New Review!</b>\n\n"
            "User <b>{reviewer}</b> left a review "
            "for your listing «{listing}».\n\n"
            "Rating: {stars} ({rating}/5)"
        ),
        "new_review_comment": "\nComment: {comment}",
        "listing_title_fallback": "listing",

        "edit_condition_prompt": "Current condition: {current}\n\nChoose a new condition:",
        "condition_new": "✨ New",
        "condition_used": "📦 Used",
        "condition_good": "👍 Good Condition",

        # ── Утилиты / format_listing_text ─────────────────────────────────
        "listing_price_label": "💰 <b>Price:</b> {price}",
        "listing_category_label": "📁 <b>Category:</b> {category}",
        "listing_condition_label": "📦 <b>Condition:</b> {condition}",
        "listing_location_label": "📍 <b>Location:</b> {location}",
        "listing_description_label": "📝 <b>Description:</b>\n{description}",
        "listing_seller_label": "\n👤 <b>Seller:</b> {name}",
        "listing_seller_rating": " ⭐ {rating:.1f} ({count} reviews)",
        "listing_views_label": "\n\n👁️ Views: {views}",
        "listing_status_label": "\n{emoji} Status: {status}",
        "status_sold_text": "Sold",

        # ── Утилиты / format_user_profile ─────────────────────────────────
        "profile_header_text": "👤 <b>Your Profile</b>\n\n",
        "profile_name_label": "<b>Name:</b> {name}\n",
        "profile_username_label": "<b>Username:</b> @{username}\n",
        "profile_phone_label": "<b>Phone:</b> {phone}\n",
        "profile_location_label": "<b>Location:</b> {location}\n",
        "profile_bio_label": "<b>About Me:</b> {bio}\n",
        "profile_rating_label": "\n⭐ <b>Rating:</b> {rating:.1f} ({count} reviews)\n",
        "profile_verified": "✅ Verified Seller\n",

        # ── Утилиты / format_review_text ──────────────────────────────────
        "reviewer_unknown": "User #{id}",

        # ── Утилиты / validate_* ──────────────────────────────────────────
        "validate_price_negative": "Price cannot be negative.",
        "validate_price_too_high": "Price cannot exceed 1 000 000 ₽.",
        "validate_price_invalid": "Please enter a valid number for the price.",
        "validate_title_empty": "Title cannot be empty.",
        "validate_title_too_short": "Title must be at least 3 characters.",
        "validate_title_too_long": "Title cannot exceed 100 characters.",
        "validate_description_too_long": "Description cannot exceed 2000 characters.",

        # ── Категории ────────────────────────────────────────────────────
        "cat_electronics": "📱 Electronics",
        "cat_clothing": "👕 Clothing & Fashion",
        "cat_home": "🏠 Home & Garden",
        "cat_vehicles": "🚗 Vehicles",
        "cat_services": "🔧 Services",
        "cat_jobs": "💼 Jobs",
        "cat_pets": "🐾 Pets",
        "cat_sports": "⚽ Sports & Hobbies",
        "cat_books": "📚 Books & Education",
        "cat_other": "📦 Other",
    },
}

# Связь ID категории с ключом i18n
CATEGORY_KEYS = {
    "electronics": "cat_electronics",
    "clothing": "cat_clothing",
    "home": "cat_home",
    "vehicles": "cat_vehicles",
    "services": "cat_services",
    "jobs": "cat_jobs",
    "pets": "cat_pets",
    "sports": "cat_sports",
    "books": "cat_books",
    "other": "cat_other",
}

# Эмодзи категорий, не зависящие от языка
CATEGORY_EMOJIS = {
    "electronics": "📱",
    "clothing": "👕",
    "home": "🏠",
    "vehicles": "🚗",
    "services": "🔧",
    "jobs": "💼",
    "pets": "🐾",
    "sports": "⚽",
    "books": "📚",
    "other": "📦",
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """
    Переводит строку по ключу на выбранный язык.
    Если ключ не найден в выбранном языке, используется русский текст.
    Поддерживает format-параметры для динамических значений.
    """
    lang_strings = STRINGS.get(lang, STRINGS["ru"])
    text = lang_strings.get(key)
    if text is None:
        text = STRINGS["ru"].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text


def get_category_name(category_id: str, lang: str = "ru") -> str:
    """Возвращает переведённое название категории."""
    key = CATEGORY_KEYS.get(category_id)
    if key:
        return t(key, lang)
    return category_id.title()


def get_category_emoji(category_id: str) -> str:
    """Возвращает эмодзи категории, не зависящее от языка."""
    return CATEGORY_EMOJIS.get(category_id, "📦")
