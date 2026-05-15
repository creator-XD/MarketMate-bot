"""
Database migration script to add admin panel columns to existing database.
Run this once to update your existing database with admin features.

Usage (from the project root):
    python scripts/migrate_database.py
"""
import asyncio
import sqlite3
import sys
import os

# Разрешаем запуск из подкаталога scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db


async def migrate():
    """Добавляет админские колонки в существующую базу данных."""
    print("=" * 60)
    print("DATABASE MIGRATION - Adding Admin Panel Columns")
    print("=" * 60)
    print()

    db = await get_db()

    # Получаем список колонок таблицы users
    cursor = await db.connection.execute("PRAGMA table_info(users)")
    user_columns = await cursor.fetchall()
    user_column_names = [col[1] for col in user_columns]

    print("Checking users table...")

    # Добавляем колонку suspension_reason, если её нет
    if "suspension_reason" not in user_column_names:
        print("  + Adding suspension_reason column...")
        await db.connection.execute("ALTER TABLE users ADD COLUMN suspension_reason TEXT")
        print("    [OK] Added suspension_reason")
    else:
        print("  [OK] suspension_reason already exists")

    # Добавляем колонку suspended_until, если её нет
    if "suspended_until" not in user_column_names:
        print("  + Adding suspended_until column...")
        await db.connection.execute("ALTER TABLE users ADD COLUMN suspended_until TIMESTAMP")
        print("    [OK] Added suspended_until")
    else:
        print("  [OK] suspended_until already exists")

    # Добавляем колонку warning_count, если её нет
    if "warning_count" not in user_column_names:
        print("  + Adding warning_count column...")
        await db.connection.execute("ALTER TABLE users ADD COLUMN warning_count INTEGER DEFAULT 0")
        print("    [OK] Added warning_count")
    else:
        print("  [OK] warning_count already exists")

    print()

    # Получаем список колонок таблицы listings
    cursor = await db.connection.execute("PRAGMA table_info(listings)")
    listing_columns = await cursor.fetchall()
    listing_column_names = [col[1] for col in listing_columns]

    print("Checking listings table...")

    # Добавляем колонку flagged, если её нет
    if "flagged" not in listing_column_names:
        print("  + Adding flagged column...")
        await db.connection.execute("ALTER TABLE listings ADD COLUMN flagged INTEGER DEFAULT 0")
        print("    [OK] Added flagged")
    else:
        print("  [OK] flagged already exists")

    # Добавляем колонку flag_reason, если её нет
    if "flag_reason" not in listing_column_names:
        print("  + Adding flag_reason column...")
        await db.connection.execute("ALTER TABLE listings ADD COLUMN flag_reason TEXT")
        print("    [OK] Added flag_reason")
    else:
        print("  [OK] flag_reason already exists")

    # Сохраняем изменения
    await db.connection.commit()

    print()
    print("=" * 60)
    print("[SUCCESS] Migration completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart the bot: python bot.py")
    print("2. Send /start to create your user account (if not done)")
    print("3. Run: python scripts/create_admin.py")
    print("4. Send /admin to access the admin panel")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(migrate())
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
