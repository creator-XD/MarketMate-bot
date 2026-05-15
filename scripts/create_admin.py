"""
Скрипт создания первого администратора.
Запускается после обновления до версии с админ-панелью.

Usage (from the project root):
    python scripts/create_admin.py
"""
import asyncio
import sys
import os

# Разрешаем запуск из подкаталога scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db
from database.models import User
from database.admin_models import AdminUser
from config import SUPER_ADMIN_ID, ADMIN_ROLES


async def create_admin():
    """Создаёт администратора в базе данных."""
    print("Creating admin user...")

    if not SUPER_ADMIN_ID:
        print("ERROR: SUPER_ADMIN_ID not set in .env file!")
        print("Please add your Telegram ID to .env as SUPER_ADMIN_ID")
        return False

    # Инициализация базы данных
    db = await get_db()
    print("Database initialized.")

    # Проверяем, существует ли пользователь
    user = await User.get_by_telegram_id(SUPER_ADMIN_ID)

    if not user:
        print(f"User with Telegram ID {SUPER_ADMIN_ID} not found in database.")
        print("Please start the bot and send /start command first to create your user account.")
        return False

    # Проверяем, существует ли администратор
    existing_admin = await AdminUser.get_by_user_id(user.id)

    if existing_admin:
        print(f"Admin user already exists!")
        print(f"  User ID: {user.id}")
        print(f"  Telegram ID: {user.telegram_id}")
        print(f"  Role: {existing_admin.role}")
        print(f"  Active: {existing_admin.is_active}")
        return True

    # Создаём администратора
    permissions = ADMIN_ROLES.get("super_admin", [])
    admin = await AdminUser.create(
        user_id=user.id,
        role="super_admin",
        permissions=permissions
    )

    print(f"✅ Admin user created successfully!")
    print(f"  User ID: {user.id}")
    print(f"  Telegram ID: {user.telegram_id}")
    print(f"  Name: {user.display_name}")
    print(f"  Role: super_admin")
    print(f"  Permissions: {len(permissions)}")
    print(f"\nYou can now access the admin panel by sending /admin command in the bot.")

    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(create_admin())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
