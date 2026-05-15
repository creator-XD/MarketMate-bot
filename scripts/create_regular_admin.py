"""
Скрипт создания обычных администраторов.

Usage:
1. Добавьте Telegram ID обычных администраторов в ADMIN_TELEGRAM_IDS в .env
2. Не добавляйте обычных администраторов в SUPER_ADMIN_ID
3. Каждый пользователь сначала должен отправить /start боту
4. Запускайте скрипт из корня проекта
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db
from database.models import User
from database.admin_models import AdminUser
from config import ADMIN_TELEGRAM_IDS, SUPER_ADMIN_ID, ADMIN_ROLES


async def create_regular_admins():
    print("Creating regular admin users...")

    await get_db()
    print("Database initialized.")

    regular_admin_ids = [
        telegram_id
        for telegram_id in ADMIN_TELEGRAM_IDS
        if telegram_id != SUPER_ADMIN_ID
    ]

    if not regular_admin_ids:
        print("No regular admin IDs found in ADMIN_TELEGRAM_IDS.")
        print("Add at least one ID besides SUPER_ADMIN_ID.")
        return False

    created_count = 0
    skipped_count = 0

    for telegram_id in regular_admin_ids:
        print("-" * 50)
        print(f"Processing Telegram ID: {telegram_id}")

        user = await User.get_by_telegram_id(telegram_id)

        if not user:
            print(f"User with Telegram ID {telegram_id} not found in database.")
            print("This user must start the bot and send /start first.")
            skipped_count += 1
            continue

        existing_admin = await AdminUser.get_by_user_id(user.id)
        permissions = ADMIN_ROLES["admin"]

        if existing_admin:
            if existing_admin.role == "super_admin":
                print("This user is already a super admin. Skipped.")
                skipped_count += 1
                continue

            await existing_admin.update(
                role="admin",
                permissions=permissions,
                is_active=1
            )

            print("Regular admin updated successfully!")
            print(f"User ID: {user.id}")
            print(f"Telegram ID: {user.telegram_id}")
            print(f"Name: {user.display_name}")
            print("Role: admin")

            created_count += 1
            continue

        admin = await AdminUser.create(
            user_id=user.id,
            role="admin",
            permissions=permissions
        )

        print("Regular admin created successfully!")
        print(f"User ID: {user.id}")
        print(f"Telegram ID: {user.telegram_id}")
        print(f"Name: {user.display_name}")
        print(f"Role: {admin.role}")
        print(f"Permissions: {len(permissions)}")

        created_count += 1

    print("-" * 50)
    print("Done.")
    print(f"Created/updated: {created_count}")
    print(f"Skipped: {skipped_count}")

    return created_count > 0


if __name__ == "__main__":
    try:
        result = asyncio.run(create_regular_admins())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)