"""
Telegram Marketplace Bot — точка входа

Прототип Telegram-бота для покупки и продажи товаров и услуг.
Построен на aiogram 3.x и SQLite с возможностью дальнейшего перехода на PostgreSQL.
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, BOT_NAME, ADMIN_TELEGRAM_IDS
from database.db import get_db, close_db
from handlers import get_all_routers
from middleware import AdminAuthMiddleware, AuditLoggerMiddleware, LanguageMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        # Раскомментируйте, чтобы дополнительно писать логи в файл:
        # logging.FileHandler("bot.log"),
    ],
)

# Уменьшаем шум от httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Выполняется при запуске бота."""
    # Инициализация базы данных
    db = await get_db()
    logger.info("Database initialized")
    
    # Получаем информацию о боте
    bot_info = await bot.get_me()
    logger.info(f"Bot started: @{bot_info.username} ({bot_info.first_name})")
    
    # Настраиваем меню команд бота
    from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

    # Команды обычного пользователя
    user_commands = [
        BotCommand(command="start", description="Start the bot / Main menu"),
        BotCommand(command="search", description="Search listings"),
        BotCommand(command="mylistings", description="View your listings"),
        BotCommand(command="favorites", description="View saved listings"),
        BotCommand(command="profile", description="View your profile"),
        BotCommand(command="help", description="Get help"),
        BotCommand(command="cancel", description="Cancel current operation"),
        BotCommand(command="english", description="Switch language to English"),
        BotCommand(command="russian", description="Переключить язык на русский"),
    ]
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())
    logger.info("Bot commands menu set for regular users")

    # Команды администраторов
    if ADMIN_TELEGRAM_IDS:
        admin_commands = user_commands + [
            BotCommand(command="admin", description="🔧 Admin Panel"),
        ]
        for admin_id in ADMIN_TELEGRAM_IDS:
            try:
                await bot.set_my_commands(
                    admin_commands,
                    scope=BotCommandScopeChat(chat_id=admin_id)
                )
            except Exception as e:
                logger.warning(f"Could not set admin commands for {admin_id}: {e}")
        logger.info(f"Admin commands set for {len(ADMIN_TELEGRAM_IDS)} admin users")


async def on_shutdown(bot: Bot):
    """Выполняется при остановке бота."""
    await close_db()
    logger.info("Database connection closed")
    logger.info("Bot stopped")


async def main():
    """Основная точка входа."""
    # Проверяем токен
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Bot token not configured! Please set BOT_TOKEN in config.py")
        sys.exit(1)
    
    # Создаём бота с HTML-разметкой по умолчанию
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    # Создаём диспетчер с хранением FSM в памяти
    # Для продакшена лучше использовать Redis-хранилище состояний
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем middleware до роутеров
    # Языковое middleware запускается первым, чтобы `lang` был доступен обработчикам
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())
    dp.message.middleware(AdminAuthMiddleware())
    dp.callback_query.middleware(AdminAuthMiddleware())
    dp.message.middleware(AuditLoggerMiddleware())
    dp.callback_query.middleware(AuditLoggerMiddleware())
    logger.info("Middleware registered (language, admin, audit)")

    # Регистрируем обработчики запуска и остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Подключаем все роутеры
    for router in get_all_routers():
        dp.include_router(router)
        logger.info(f"Registered router: {router.name}")
    
    # Запускаем polling
    logger.info(f"Starting {BOT_NAME}...")
    
    try:
        # Удаляем webhook, если он был установлен, и запускаем polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
