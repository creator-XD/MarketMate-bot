"""
Admin-specific database models for the Telegram Marketplace Bot.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import json
from .db import get_db
from .models import User


@dataclass
class AdminUser:
    """Модель администратора."""
    id: int
    user_id: int
    role: str
    permissions: List[str]
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    # Связанные данные
    user: Optional[User] = None

    @classmethod
    def from_row(cls, row) -> Optional["AdminUser"]:
        """Создаёт AdminUser из строки базы данных."""
        if row is None:
            return None

        # Разбираем JSON с правами
        permissions = []
        if row["permissions"]:
            try:
                permissions = json.loads(row["permissions"])
            except (json.JSONDecodeError, TypeError):
                permissions = []

        return cls(
            id=row["id"],
            user_id=row["user_id"],
            role=row["role"],
            permissions=permissions,
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @classmethod
    async def get_by_user_id(cls, user_id: int) -> Optional["AdminUser"]:
        """Получает администратора по ID пользователя."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT * FROM admin_users WHERE user_id = ?",
            (user_id,)
        )
        admin = cls.from_row(row)
        if admin:
            admin.user = await User.get_by_id(user_id)
        return admin

    @classmethod
    async def get_by_telegram_id(cls, telegram_id: int) -> Optional["AdminUser"]:
        """Получает администратора по Telegram ID."""
        db = await get_db()
        row = await db.fetch_one(
            """
            SELECT a.* FROM admin_users a
            JOIN users u ON a.user_id = u.id
            WHERE u.telegram_id = ?
            """,
            (telegram_id,)
        )
        admin = cls.from_row(row)
        if admin:
            admin.user = await User.get_by_telegram_id(telegram_id)
        return admin

    @classmethod
    async def create(
        cls,
        user_id: int,
        role: str,
        permissions: List[str] = None
    ) -> "AdminUser":
        """Создаёт нового администратора."""
        db = await get_db()

        # Преобразуем права в JSON
        permissions_json = json.dumps(permissions or [])

        cursor = await db.execute(
            """
            INSERT INTO admin_users (user_id, role, permissions)
            VALUES (?, ?, ?)
            """,
            (user_id, role, permissions_json)
        )

        row = await db.fetch_one(
            "SELECT * FROM admin_users WHERE id = ?",
            (cursor.lastrowid,)
        )
        return cls.from_row(row)

    async def update(self, **kwargs) -> bool:
        """Обновляет поля администратора."""
        if not kwargs:
            return False

        # Преобразуем права в JSON если они переданы
        if "permissions" in kwargs and isinstance(kwargs["permissions"], list):
            kwargs["permissions"] = json.dumps(kwargs["permissions"])

        db = await get_db()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [self.id]

        await db.execute(
            f"UPDATE admin_users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            tuple(values)
        )
        return True

    def has_permission(self, permission: str) -> bool:
        """Проверяет наличие конкретного права у администратора."""
        if not self.is_active:
            return False
        return permission in self.permissions

    @classmethod
    async def get_all(cls, active_only: bool = True) -> List["AdminUser"]:
        """Получает всех администраторов."""
        db = await get_db()
        if active_only:
            rows = await db.fetch_all(
                "SELECT * FROM admin_users WHERE is_active = 1 ORDER BY created_at DESC"
            )
        else:
            rows = await db.fetch_all(
                "SELECT * FROM admin_users ORDER BY created_at DESC"
            )

        admins = [cls.from_row(row) for row in rows]

        # Загружаем данные пользователя
        for admin in admins:
            admin.user = await User.get_by_id(admin.user_id)

        return admins


@dataclass
class AdminAuditLog:
    """Модель журнала действий администратора."""
    id: int
    admin_id: int
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    details: dict
    created_at: Optional[datetime]
    # Связанные данные
    admin_user: Optional[User] = None

    @classmethod
    def from_row(cls, row) -> Optional["AdminAuditLog"]:
        """Создаёт AdminAuditLog из строки базы данных."""
        if row is None:
            return None

        # Разбираем JSON с деталями
        details = {}
        if row["details"]:
            try:
                details = json.loads(row["details"])
            except (json.JSONDecodeError, TypeError):
                details = {}

        return cls(
            id=row["id"],
            admin_id=row["admin_id"],
            action=row["action"],
            target_type=row["target_type"],
            target_id=row["target_id"],
            details=details,
            created_at=row["created_at"],
        )

    @classmethod
    async def create(
        cls,
        admin_id: int,
        action: str,
        target_type: str = None,
        target_id: int = None,
        details: dict = None
    ) -> "AdminAuditLog":
        """Создаёт новую запись журнала аудита."""
        db = await get_db()

        # Преобразуем детали в JSON
        details_json = json.dumps(details or {})

        cursor = await db.execute(
            """
            INSERT INTO admin_audit_log (admin_id, action, target_type, target_id, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (admin_id, action, target_type, target_id, details_json)
        )

        row = await db.fetch_one(
            "SELECT * FROM admin_audit_log WHERE id = ?",
            (cursor.lastrowid,)
        )
        return cls.from_row(row)

    @classmethod
    async def get_recent(
        cls,
        limit: int = 50,
        offset: int = 0,
        admin_id: int = None,
        action: str = None,
        actions: List[str] = None
    ) -> List["AdminAuditLog"]:
        """Получает последние записи журнала аудита.

        Аргументы:
            limit: Max number of entries to return.
            offset: Number of entries to skip (for pagination).
            admin_id: Filter by specific admin.
            action: Filter by single action type (exact match).
            actions: Filter by multiple action types (IN match).
        """
        db = await get_db()

        conditions = []
        params = []

        if admin_id:
            conditions.append("admin_id = ?")
            params.append(admin_id)

        if actions:
            placeholders = ",".join(["?" for _ in actions])
            conditions.append(f"action IN ({placeholders})")
            params.extend(actions)
        elif action:
            conditions.append("action = ?")
            params.append(action)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.extend([limit, offset])

        rows = await db.fetch_all(
            f"""
            SELECT * FROM admin_audit_log
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params)
        )

        logs = [cls.from_row(row) for row in rows]

        # Загружаем данные администратора
        for log in logs:
            log.admin_user = await User.get_by_id(log.admin_id)

        return logs

    @classmethod
    async def count(cls, admin_id: int = None, actions: List[str] = None) -> int:
        """Подсчитывает записи журнала аудита по фильтрам.

        Аргументы:
            admin_id: Filter by specific admin.
            actions: Filter by multiple action types.
        """
        db = await get_db()

        conditions = []
        params = []

        if admin_id:
            conditions.append("admin_id = ?")
            params.append(admin_id)

        if actions:
            placeholders = ",".join(["?" for _ in actions])
            conditions.append(f"action IN ({placeholders})")
            params.extend(actions)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        row = await db.fetch_one(
            f"SELECT COUNT(*) as count FROM admin_audit_log WHERE {where_clause}",
            tuple(params) if params else None
        )
        return row["count"] if row else 0

    @classmethod
    async def search(
        cls,
        target_type: str = None,
        target_id: int = None,
        limit: int = 50,
        offset: int = 0
    ) -> List["AdminAuditLog"]:
        """Ищет записи аудита по цели."""
        db = await get_db()

        conditions = []
        params = []

        if target_type:
            conditions.append("target_type = ?")
            params.append(target_type)

        if target_id:
            conditions.append("target_id = ?")
            params.append(target_id)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.extend([limit, offset])

        rows = await db.fetch_all(
            f"""
            SELECT * FROM admin_audit_log
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params)
        )

        logs = [cls.from_row(row) for row in rows]

        # Загружаем данные администратора
        for log in logs:
            log.admin_user = await User.get_by_id(log.admin_id)

        return logs


@dataclass
class UserWarning:
    """Модель предупреждения пользователя."""
    id: int
    user_id: int
    admin_id: int
    reason: str
    severity: str
    is_active: bool
    created_at: Optional[datetime]
    expires_at: Optional[datetime]
    # Связанные данные
    user: Optional[User] = None
    admin_user: Optional[User] = None

    @classmethod
    def from_row(cls, row) -> Optional["UserWarning"]:
        """Создаёт UserWarning из строки базы данных."""
        if row is None:
            return None

        return cls(
            id=row["id"],
            user_id=row["user_id"],
            admin_id=row["admin_id"],
            reason=row["reason"],
            severity=row["severity"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            expires_at=row["expires_at"],
        )

    @classmethod
    async def create(
        cls,
        user_id: int,
        admin_id: int,
        reason: str,
        severity: str = "low",
        expires_at: datetime = None
    ) -> "UserWarning":
        """Создаёт новое предупреждение пользователя."""
        db = await get_db()

        cursor = await db.execute(
            """
            INSERT INTO user_warnings (user_id, admin_id, reason, severity, expires_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, admin_id, reason, severity, expires_at)
        )

        # Увеличиваем счётчик предупреждений пользователя
        await db.execute(
            "UPDATE users SET warning_count = warning_count + 1 WHERE id = ?",
            (user_id,)
        )

        row = await db.fetch_one(
            "SELECT * FROM user_warnings WHERE id = ?",
            (cursor.lastrowid,)
        )
        return cls.from_row(row)

    @classmethod
    async def get_by_user_id(cls, user_id: int, active_only: bool = True) -> List["UserWarning"]:
        """Получает все предупреждения пользователя."""
        db = await get_db()

        if active_only:
            rows = await db.fetch_all(
                """
                SELECT * FROM user_warnings
                WHERE user_id = ? AND is_active = 1
                ORDER BY created_at DESC
                """,
                (user_id,)
            )
        else:
            rows = await db.fetch_all(
                """
                SELECT * FROM user_warnings
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,)
            )

        warnings = [cls.from_row(row) for row in rows]

        # Загружаем связанные данные
        for warning in warnings:
            warning.user = await User.get_by_id(warning.user_id)
            warning.admin_user = await User.get_by_id(warning.admin_id)

        return warnings

    async def deactivate(self) -> bool:
        """Деактивирует это предупреждение."""
        db = await get_db()
        await db.execute(
            "UPDATE user_warnings SET is_active = 0 WHERE id = ?",
            (self.id,)
        )
        return True

    @classmethod
    async def count_active_by_user(cls, user_id: int) -> int:
        """Подсчитывает активные предупреждения пользователя."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT COUNT(*) as count FROM user_warnings WHERE user_id = ? AND is_active = 1",
            (user_id,)
        )
        return row["count"] if row else 0
