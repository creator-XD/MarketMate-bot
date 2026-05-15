"""
Модели и операции базы данных Telegram Marketplace Bot.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import logging
from .db import get_db

logger = logging.getLogger(__name__)


@dataclass
class User:
    """Модель пользователя."""
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    rating: float = 0.0
    rating_count: int = 0
    suspension_reason: Optional[str] = None
    suspended_until: Optional[datetime] = None
    warning_count: int = 0
    language: str = "ru"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> Optional["User"]:
        """Создаёт User из строки базы данных."""
        if row is None:
            return None

        # Обрабатываем новые админские поля, которых может не быть в старых схемах БД
        try:
            suspension_reason = row["suspension_reason"]
        except (KeyError, IndexError):
            suspension_reason = None

        try:
            suspended_until = row["suspended_until"]
        except (KeyError, IndexError):
            suspended_until = None

        try:
            warning_count = row["warning_count"]
        except (KeyError, IndexError):
            warning_count = 0

        try:
            language = row["language"] or "ru"
        except (KeyError, IndexError):
            language = "ru"

        return cls(
            id=row["id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            phone=row["phone"],
            location=row["location"],
            bio=row["bio"],
            is_active=bool(row["is_active"]),
            is_verified=bool(row["is_verified"]),
            rating=row["rating"],
            rating_count=row["rating_count"],
            suspension_reason=suspension_reason,
            suspended_until=suspended_until,
            warning_count=warning_count,
            language=language,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    
    @classmethod
    async def get_by_telegram_id(cls, telegram_id: int) -> Optional["User"]:
        """Получает пользователя по Telegram ID."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        return cls.from_row(row)
    
    @classmethod
    async def get_by_id(cls, user_id: int) -> Optional["User"]:
        """Получает пользователя по внутреннему ID."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        return cls.from_row(row)
    
    @classmethod
    async def create(
        cls,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> "User":
        """Создаёт нового пользователя."""
        db = await get_db()
        cursor = await db.execute(
            """
            INSERT INTO users (telegram_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
            """,
            (telegram_id, username, first_name, last_name)
        )
        return await cls.get_by_id(cursor.lastrowid)
    
    @classmethod
    async def get_or_create(
        cls,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> "User":
        """Получает существующего пользователя или создаёт нового."""
        user = await cls.get_by_telegram_id(telegram_id)
        if user is None:
            user = await cls.create(telegram_id, username, first_name, last_name)
        else:
            # Обновляем данные пользователя, если они изменились
            await user.update(username=username, first_name=first_name, last_name=last_name)
            user = await cls.get_by_telegram_id(telegram_id)
        return user
    
    async def update(self, **kwargs) -> bool:
        """Обновляет поля пользователя."""
        if not kwargs:
            return False

        db = await get_db()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [self.id]

        await db.execute(
            f"UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            tuple(values)
        )
        return True

    @classmethod
    async def get_by_username(cls, username: str) -> Optional["User"]:
        """Получает пользователя по username без учёта регистра."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?)",
            (username,)
        )
        return cls.from_row(row)

    @classmethod
    async def search_by_display_name(cls, name: str) -> Optional["User"]:
        """Ищет пользователя по отображаемому имени, имени, фамилии или их сочетанию."""
        db = await get_db()
        # Пробуем найти совпадение по first_name, last_name или их сочетанию
        rows = await db.fetch_all(
            """
            SELECT * FROM users
            WHERE LOWER(first_name) LIKE LOWER(?)
               OR LOWER(last_name) LIKE LOWER(?)
               OR LOWER(first_name || ' ' || last_name) LIKE LOWER(?)
            LIMIT 1
            """,
            (f"%{name}%", f"%{name}%", f"%{name}%")
        )
        if rows:
            return cls.from_row(rows[0])
        return None

    @property
    def display_name(self) -> str:
        """Возвращает отображаемое имя пользователя."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        return f"User #{self.telegram_id}"

    @classmethod
    async def get_all(
        cls,
        status: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List["User"]:
        """Получает пользователей с необязательными фильтрами для админ-панели."""
        db = await get_db()
        conditions = []
        params = []

        if status == "active":
            conditions.append("is_active = 1")
        elif status == "blocked":
            conditions.append("is_active = 0")
        elif status == "verified":
            conditions.append("is_verified = 1")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.extend([limit, offset])

        rows = await db.fetch_all(
            f"""
            SELECT * FROM users
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params)
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    async def count_all(cls, status: str = None) -> int:
        """Подсчитывает пользователей с необязательными фильтрами для админ-панели."""
        db = await get_db()
        conditions = []
        params = []

        if status == "active":
            conditions.append("is_active = 1")
        elif status == "blocked":
            conditions.append("is_active = 0")
        elif status == "verified":
            conditions.append("is_verified = 1")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        row = await db.fetch_one(
            f"SELECT COUNT(*) as count FROM users WHERE {where_clause}",
            tuple(params)
        )
        return row["count"] if row else 0

    @classmethod
    async def get_statistics(cls) -> dict:
        """Получает статистику пользователей для админ-панели."""
        db = await get_db()

        # Всего пользователей
        total = await db.fetch_one("SELECT COUNT(*) as count FROM users")
        # Активные пользователи
        active = await db.fetch_one("SELECT COUNT(*) as count FROM users WHERE is_active = 1")
        # Заблокированные пользователи
        blocked = await db.fetch_one("SELECT COUNT(*) as count FROM users WHERE is_active = 0")
        # Верифицированные пользователи
        verified = await db.fetch_one("SELECT COUNT(*) as count FROM users WHERE is_verified = 1")
        # Новые пользователи сегодня
        new_today = await db.fetch_one(
            "SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = DATE('now')"
        )
        # Новые пользователи за неделю
        new_week = await db.fetch_one(
            "SELECT COUNT(*) as count FROM users WHERE created_at >= DATE('now', '-7 days')"
        )

        return {
            "total": total["count"] if total else 0,
            "active": active["count"] if active else 0,
            "blocked": blocked["count"] if blocked else 0,
            "verified": verified["count"] if verified else 0,
            "new_today": new_today["count"] if new_today else 0,
            "new_week": new_week["count"] if new_week else 0,
        }


@dataclass
class Listing:
    """Модель объявления."""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    price: float
    currency: str
    category: str
    location: Optional[str]
    status: str
    condition: str
    views: int
    flagged: int
    flag_reason: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    # Связанные данные (загружаются отдельно)
    photos: Optional[List["ListingPhoto"]] = None
    user: Optional[User] = None
    
    @classmethod
    def from_row(cls, row) -> Optional["Listing"]:
        """Создаёт Listing из строки базы данных."""
        if row is None:
            return None

        # Обрабатываем поля, которых может не быть в старых схемах БД
        try:
            flagged = row["flagged"]
        except (KeyError, IndexError):
            flagged = 0

        try:
            flag_reason = row["flag_reason"]
        except (KeyError, IndexError):
            flag_reason = None

        try:
            condition = row["condition"] or "new"
        except (KeyError, IndexError):
            condition = "new"

        return cls(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            description=row["description"],
            price=row["price"],
            currency=row["currency"],
            category=row["category"],
            location=row["location"],
            status=row["status"],
            condition=condition,
            views=row["views"],
            flagged=flagged,
            flag_reason=flag_reason,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    
    @classmethod
    async def get_by_id(cls, listing_id: int, with_photos: bool = False, with_user: bool = False) -> Optional["Listing"]:
        """Получает объявление по ID."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT * FROM listings WHERE id = ?",
            (listing_id,)
        )
        listing = cls.from_row(row)
        
        if listing and with_photos:
            listing.photos = await ListingPhoto.get_by_listing_id(listing_id)
        
        if listing and with_user:
            listing.user = await User.get_by_id(listing.user_id)
        
        return listing
    
    @classmethod
    async def get_by_user(cls, user_id: int, status: str = None) -> List["Listing"]:
        """Получает все объявления пользователя."""
        db = await get_db()
        if status:
            rows = await db.fetch_all(
                "SELECT * FROM listings WHERE user_id = ? AND status = ? ORDER BY created_at DESC",
                (user_id, status)
            )
        else:
            rows = await db.fetch_all(
                "SELECT * FROM listings WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    async def create(
        cls,
        user_id: int,
        title: str,
        description: str,
        price: float,
        category: str,
        currency: str = "USD",
        location: str = None,
        condition: str = "new",
    ) -> "Listing":
        """Создаёт новое объявление."""
        db = await get_db()
        cursor = await db.execute(
            """
            INSERT INTO listings (user_id, title, description, price, category, currency, location, condition)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, title, description, price, category, currency, location, condition)
        )
        return await cls.get_by_id(cursor.lastrowid)
    
    async def update(self, **kwargs) -> bool:
        """Обновляет поля объявления."""
        if not kwargs:
            return False
        
        db = await get_db()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [self.id]
        
        await db.execute(
            f"UPDATE listings SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            tuple(values)
        )
        return True
    
    async def delete(self) -> bool:
        """Выполняет мягкое удаление объявления."""
        return await self.update(status="deleted")
    
    async def increment_views(self) -> None:
        """Увеличивает счётчик просмотров."""
        db = await get_db()
        await db.execute(
            "UPDATE listings SET views = views + 1 WHERE id = ?",
            (self.id,)
        )
    
    @classmethod
    async def search(
        cls,
        query: str = None,
        category: str = None,
        min_price: float = None,
        max_price: float = None,
        seller_id: int = None,
        location: str = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List["Listing"]:
        """Ищет объявления с фильтрами."""
        db = await get_db()
        conditions = ["status = 'active'"]
        params = []

        if query:
            conditions.append("(title LIKE ? OR description LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])

        if category:
            conditions.append("category = ?")
            params.append(category)

        if seller_id:
            conditions.append("user_id = ?")
            params.append(seller_id)

        if min_price is not None:
            conditions.append("price >= ?")
            params.append(min_price)

        if max_price is not None:
            conditions.append("price <= ?")
            params.append(max_price)

        if location:
            conditions.append("location LIKE ?")
            params.append(f"%{location}%")
        
        where_clause = " AND ".join(conditions)
        params.extend([limit, offset])
        
        rows = await db.fetch_all(
            f"""
            SELECT * FROM listings 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    async def count_search(
        cls,
        query: str = None,
        category: str = None,
        min_price: float = None,
        max_price: float = None,
        seller_id: int = None,
        location: str = None,
    ) -> int:
        """Подсчитывает объявления, подходящие под критерии поиска."""
        db = await get_db()
        conditions = ["status = 'active'"]
        params = []

        if query:
            conditions.append("(title LIKE ? OR description LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])

        if category:
            conditions.append("category = ?")
            params.append(category)

        if seller_id:
            conditions.append("user_id = ?")
            params.append(seller_id)

        if min_price is not None:
            conditions.append("price >= ?")
            params.append(min_price)

        if max_price is not None:
            conditions.append("price <= ?")
            params.append(max_price)

        if location:
            conditions.append("location LIKE ?")
            params.append(f"%{location}%")
        
        where_clause = " AND ".join(conditions)
        
        row = await db.fetch_one(
            f"SELECT COUNT(*) as count FROM listings WHERE {where_clause}",
            tuple(params)
        )
        return row["count"] if row else 0
    
    @classmethod
    async def get_recent(cls, limit: int = 10) -> List["Listing"]:
        """Получает последние активные объявления."""
        db = await get_db()
        rows = await db.fetch_all(
            "SELECT * FROM listings WHERE status = 'active' ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    async def get_by_category(cls, category: str, limit: int = 10, offset: int = 0) -> List["Listing"]:
        """Получает объявления по категории."""
        db = await get_db()
        rows = await db.fetch_all(
            """
            SELECT * FROM listings
            WHERE category = ? AND status = 'active'
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (category, limit, offset)
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    async def get_all_admin(
        cls,
        status: str = None,
        category: str = None,
        flagged_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List["Listing"]:
        """Получает объявления с фильтрами для админ-панели."""
        db = await get_db()
        conditions = []
        params = []

        if status:
            conditions.append("status = ?")
            params.append(status)

        if category:
            conditions.append("category = ?")
            params.append(category)

        if flagged_only:
            conditions.append("flagged = 1")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.extend([limit, offset])

        rows = await db.fetch_all(
            f"""
            SELECT * FROM listings
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params)
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    async def count_all_admin(
        cls,
        status: str = None,
        category: str = None,
        flagged_only: bool = False
    ) -> int:
        """Подсчитывает объявления с фильтрами для админ-панели."""
        db = await get_db()
        conditions = []
        params = []

        if status:
            conditions.append("status = ?")
            params.append(status)

        if category:
            conditions.append("category = ?")
            params.append(category)

        if flagged_only:
            conditions.append("flagged = 1")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        row = await db.fetch_one(
            f"SELECT COUNT(*) as count FROM listings WHERE {where_clause}",
            tuple(params)
        )
        return row["count"] if row else 0

    @classmethod
    async def get_statistics(cls) -> dict:
        """Получает статистику объявлений для админ-панели."""
        db = await get_db()

        # Всего объявлений
        total = await db.fetch_one("SELECT COUNT(*) as count FROM listings")
        # Активные объявления
        active = await db.fetch_one("SELECT COUNT(*) as count FROM listings WHERE status = 'active'")
        # Проданные объявления
        sold = await db.fetch_one("SELECT COUNT(*) as count FROM listings WHERE status = 'sold'")
        # Удалённые объявления
        deleted = await db.fetch_one("SELECT COUNT(*) as count FROM listings WHERE status = 'deleted'")
        # Отмеченные объявления
        flagged = await db.fetch_one("SELECT COUNT(*) as count FROM listings WHERE flagged = 1")
        # Новые объявления сегодня
        new_today = await db.fetch_one(
            "SELECT COUNT(*) as count FROM listings WHERE DATE(created_at) = DATE('now')"
        )
        # Новые объявления за неделю
        new_week = await db.fetch_one(
            "SELECT COUNT(*) as count FROM listings WHERE created_at >= DATE('now', '-7 days')"
        )

        return {
            "total": total["count"] if total else 0,
            "active": active["count"] if active else 0,
            "sold": sold["count"] if sold else 0,
            "deleted": deleted["count"] if deleted else 0,
            "flagged": flagged["count"] if flagged else 0,
            "new_today": new_today["count"] if new_today else 0,
            "new_week": new_week["count"] if new_week else 0,
        }


@dataclass
class ListingPhoto:
    """Модель фотографии объявления."""
    id: int
    listing_id: int
    file_id: str
    file_unique_id: str
    is_primary: bool
    created_at: Optional[datetime]
    
    @classmethod
    def from_row(cls, row) -> Optional["ListingPhoto"]:
        """Создаёт ListingPhoto из строки базы данных."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            listing_id=row["listing_id"],
            file_id=row["file_id"],
            file_unique_id=row["file_unique_id"],
            is_primary=bool(row["is_primary"]),
            created_at=row["created_at"],
        )
    
    @classmethod
    async def get_by_listing_id(cls, listing_id: int) -> List["ListingPhoto"]:
        """Получает все фотографии объявления."""
        db = await get_db()
        rows = await db.fetch_all(
            "SELECT * FROM listing_photos WHERE listing_id = ? ORDER BY is_primary DESC, id ASC",
            (listing_id,)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    async def create(cls, listing_id: int, file_id: str, file_unique_id: str, is_primary: bool = False) -> "ListingPhoto":
        """Создаёт новую фотографию объявления."""
        db = await get_db()
        cursor = await db.execute(
            """
            INSERT INTO listing_photos (listing_id, file_id, file_unique_id, is_primary)
            VALUES (?, ?, ?, ?)
            """,
            (listing_id, file_id, file_unique_id, is_primary)
        )
        row = await db.fetch_one("SELECT * FROM listing_photos WHERE id = ?", (cursor.lastrowid,))
        return cls.from_row(row)
    
    @classmethod
    async def delete_by_listing_id(cls, listing_id: int) -> None:
        """Удаляет все фотографии объявления."""
        db = await get_db()
        await db.execute("DELETE FROM listing_photos WHERE listing_id = ?", (listing_id,))


@dataclass
class Favorite:
    """Модель избранного."""
    id: int
    user_id: int
    listing_id: int
    created_at: Optional[datetime]
    
    @classmethod
    def from_row(cls, row) -> Optional["Favorite"]:
        """Создаёт Favorite из строки базы данных."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            listing_id=row["listing_id"],
            created_at=row["created_at"],
        )
    
    @classmethod
    async def add(cls, user_id: int, listing_id: int) -> Optional["Favorite"]:
        """Добавляет объявление в избранное."""
        db = await get_db()
        try:
            cursor = await db.execute(
                "INSERT INTO favorites (user_id, listing_id) VALUES (?, ?)",
                (user_id, listing_id)
            )
            row = await db.fetch_one("SELECT * FROM favorites WHERE id = ?", (cursor.lastrowid,))
            return cls.from_row(row)
        except Exception:
            return None  # Уже в избранном
    
    @classmethod
    async def remove(cls, user_id: int, listing_id: int) -> bool:
        """Удаляет объявление из избранного."""
        db = await get_db()
        await db.execute(
            "DELETE FROM favorites WHERE user_id = ? AND listing_id = ?",
            (user_id, listing_id)
        )
        return True
    
    @classmethod
    async def is_favorite(cls, user_id: int, listing_id: int) -> bool:
        """Проверяет, находится ли объявление в избранном пользователя."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT id FROM favorites WHERE user_id = ? AND listing_id = ?",
            (user_id, listing_id)
        )
        return row is not None
    
    @classmethod
    async def get_user_favorites(cls, user_id: int) -> List[Listing]:
        """Получает избранные объявления пользователя."""
        db = await get_db()
        rows = await db.fetch_all(
            """
            SELECT l.* FROM listings l
            JOIN favorites f ON l.id = f.listing_id
            WHERE f.user_id = ? AND l.status = 'active'
            ORDER BY f.created_at DESC
            """,
            (user_id,)
        )
        return [Listing.from_row(row) for row in rows]


@dataclass
class Message:
    """Модель сообщения между покупателем и продавцом."""
    id: int
    listing_id: Optional[int]
    sender_id: int
    receiver_id: int
    message_text: Optional[str]
    is_read: bool
    created_at: Optional[datetime]
    
    @classmethod
    def from_row(cls, row) -> Optional["Message"]:
        """Создаёт Message из строки базы данных."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            listing_id=row["listing_id"],
            sender_id=row["sender_id"],
            receiver_id=row["receiver_id"],
            message_text=row["message_text"],
            is_read=bool(row["is_read"]),
            created_at=row["created_at"],
        )
    
    @classmethod
    async def create(cls, sender_id: int, receiver_id: int, message_text: str, listing_id: int = None) -> "Message":
        """Создаёт новое сообщение."""
        db = await get_db()
        cursor = await db.execute(
            """
            INSERT INTO messages (listing_id, sender_id, receiver_id, message_text)
            VALUES (?, ?, ?, ?)
            """,
            (listing_id, sender_id, receiver_id, message_text)
        )
        row = await db.fetch_one("SELECT * FROM messages WHERE id = ?", (cursor.lastrowid,))
        return cls.from_row(row)
    
    @classmethod
    async def get_unread_count(cls, user_id: int) -> int:
        """Получает количество непрочитанных сообщений пользователя."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT COUNT(*) as count FROM messages WHERE receiver_id = ? AND is_read = 0",
            (user_id,)
        )
        return row["count"] if row else 0


@dataclass
class Transaction:
    """Модель транзакции (заглушка для будущей платёжной интеграции)."""
    id: int
    listing_id: int
    buyer_id: int
    seller_id: int
    amount: float
    currency: str
    status: str
    payment_method: Optional[str]
    payment_id: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    @classmethod
    def from_row(cls, row) -> Optional["Transaction"]:
        """Создаёт Transaction из строки базы данных."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            listing_id=row["listing_id"],
            buyer_id=row["buyer_id"],
            seller_id=row["seller_id"],
            amount=row["amount"],
            currency=row["currency"],
            status=row["status"],
            payment_method=row["payment_method"],
            payment_id=row["payment_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    
    @classmethod
    async def create(
        cls,
        listing_id: int,
        buyer_id: int,
        seller_id: int,
        amount: float,
        currency: str = "USD",
    ) -> "Transaction":
        """Создаёт новую транзакцию (заглушка)."""
        db = await get_db()
        cursor = await db.execute(
            """
            INSERT INTO transactions (listing_id, buyer_id, seller_id, amount, currency)
            VALUES (?, ?, ?, ?, ?)
            """,
            (listing_id, buyer_id, seller_id, amount, currency)
        )
        row = await db.fetch_one("SELECT * FROM transactions WHERE id = ?", (cursor.lastrowid,))
        return cls.from_row(row)

    @classmethod
    async def get_all(
        cls,
        status: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List["Transaction"]:
        """Получает транзакции с фильтрами для админ-панели."""
        db = await get_db()

        if status:
            rows = await db.fetch_all(
                """
                SELECT * FROM transactions
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (status, limit, offset)
            )
        else:
            rows = await db.fetch_all(
                """
                SELECT * FROM transactions
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )

        return [cls.from_row(row) for row in rows]

    @classmethod
    async def count_all(cls, status: str = None) -> int:
        """Подсчитывает транзакции с фильтрами для админ-панели."""
        db = await get_db()

        if status:
            row = await db.fetch_one(
                "SELECT COUNT(*) as count FROM transactions WHERE status = ?",
                (status,)
            )
        else:
            row = await db.fetch_one("SELECT COUNT(*) as count FROM transactions")

        return row["count"] if row else 0

    @classmethod
    async def get_statistics(cls) -> dict:
        """Получает статистику транзакций для админ-панели."""
        db = await get_db()

        # Всего транзакций
        total = await db.fetch_one("SELECT COUNT(*) as count FROM transactions")
        # Ожидают обработки
        pending = await db.fetch_one("SELECT COUNT(*) as count FROM transactions WHERE status = 'pending'")
        # Завершены
        completed = await db.fetch_one("SELECT COUNT(*) as count FROM transactions WHERE status = 'completed'")
        # Отменены
        cancelled = await db.fetch_one("SELECT COUNT(*) as count FROM transactions WHERE status = 'cancelled'")

        return {
            "total": total["count"] if total else 0,
            "pending": pending["count"] if pending else 0,
            "completed": completed["count"] if completed else 0,
            "cancelled": cancelled["count"] if cancelled else 0,
        }


@dataclass
class Review:
    """Модель отзыва о продавце."""
    id: int
    reviewer_id: int
    seller_id: int
    listing_id: Optional[int]
    rating: int
    comment: Optional[str]
    created_at: Optional[datetime]

    @classmethod
    def from_row(cls, row) -> Optional["Review"]:
        """Создаёт Review из строки базы данных."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            reviewer_id=row["reviewer_id"],
            seller_id=row["seller_id"],
            listing_id=row["listing_id"],
            rating=row["rating"],
            comment=row["comment"],
            created_at=row["created_at"],
        )

    @classmethod
    async def create(
        cls,
        reviewer_id: int,
        seller_id: int,
        listing_id: int,
        rating: int,
        comment: Optional[str] = None,
    ) -> Optional["Review"]:
        """Создаёт новый отзыв и пересчитывает рейтинг продавца."""
        db = await get_db()
        try:
            cursor = await db.execute(
                """
                INSERT INTO reviews (reviewer_id, seller_id, listing_id, rating, comment)
                VALUES (?, ?, ?, ?, ?)
                """,
                (reviewer_id, seller_id, listing_id, rating, comment)
            )

            # Пересчитываем средний рейтинг продавца
            row = await db.fetch_one(
                "SELECT AVG(rating) as avg_rating, COUNT(*) as cnt FROM reviews WHERE seller_id = ?",
                (seller_id,)
            )
            if row:
                await db.execute(
                    "UPDATE users SET rating = ?, rating_count = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (round(row["avg_rating"], 2), row["cnt"], seller_id)
                )

            result_row = await db.fetch_one("SELECT * FROM reviews WHERE id = ?", (cursor.lastrowid,))
            return cls.from_row(result_row)
        except Exception as e:
            logger.exception("Failed to create review")
            return None

    @classmethod
    async def get_by_seller(cls, seller_id: int, limit: int = 10, offset: int = 0) -> List["Review"]:
        """Получает отзывы о продавце."""
        db = await get_db()
        rows = await db.fetch_all(
            """
            SELECT * FROM reviews
            WHERE seller_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (seller_id, limit, offset)
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    async def count_by_seller(cls, seller_id: int) -> int:
        """Подсчитывает отзывы о продавце."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT COUNT(*) as count FROM reviews WHERE seller_id = ?",
            (seller_id,)
        )
        return row["count"] if row else 0

    @classmethod
    async def get_by_id(cls, review_id: int) -> Optional["Review"]:
        """Получает отзыв по ID."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT * FROM reviews WHERE id = ?",
            (review_id,)
        )
        return cls.from_row(row)

    @classmethod
    async def delete(cls, review_id: int, seller_id: int) -> bool:
        """Удаляет отзыв и пересчитывает рейтинг продавца."""
        db = await get_db()
        try:
            await db.execute("DELETE FROM reviews WHERE id = ?", (review_id,))

            # Пересчитываем средний рейтинг продавца
            row = await db.fetch_one(
                "SELECT AVG(rating) as avg_rating, COUNT(*) as cnt FROM reviews WHERE seller_id = ?",
                (seller_id,)
            )
            if row and row["cnt"] > 0:
                await db.execute(
                    "UPDATE users SET rating = ?, rating_count = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (round(row["avg_rating"], 2), row["cnt"], seller_id)
                )
            else:
                await db.execute(
                    "UPDATE users SET rating = 0, rating_count = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (seller_id,)
                )
            return True
        except Exception:
            logger.exception("Failed to delete review")
            return False

    @classmethod
    async def get_all_admin(cls, limit: int = 50, offset: int = 0) -> List["Review"]:
        """Получает отзывы с пагинацией для админ-панели."""
        db = await get_db()
        rows = await db.fetch_all(
            """
            SELECT * FROM reviews
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    async def count_all(cls) -> int:
        """Подсчитывает все отзывы."""
        db = await get_db()
        row = await db.fetch_one("SELECT COUNT(*) as count FROM reviews")
        return row["count"] if row else 0

    @classmethod
    async def get_by_reviewer_and_listing(cls, reviewer_id: int, listing_id: int) -> Optional["Review"]:
        """Проверяет, оставлял ли пользователь отзыв по этому объявлению."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT * FROM reviews WHERE reviewer_id = ? AND listing_id = ?",
            (reviewer_id, listing_id)
        )
        return cls.from_row(row)


@dataclass
class UserReport:
    """Жалоба пользователя на объявление или другого пользователя."""
    id: int
    reporter_id: int
    target_type: str   # "listing" или "user"
    target_id: int
    reason: str
    comment: Optional[str]
    status: str
    created_at: Optional[datetime]

    @classmethod
    def from_row(cls, row) -> Optional["UserReport"]:
        if row is None:
            return None
        return cls(
            id=row["id"],
            reporter_id=row["reporter_id"],
            target_type=row["target_type"],
            target_id=row["target_id"],
            reason=row["reason"],
            comment=row["comment"],
            status=row["status"],
            created_at=row["created_at"],
        )

    @classmethod
    async def create(
        cls,
        reporter_id: int,
        target_type: str,
        target_id: int,
        reason: str,
        comment: str = None,
    ) -> "UserReport":
        """Создаёт новую жалобу и выбрасывает ошибку при дубле."""
        db = await get_db()
        cursor = await db.execute(
            """
            INSERT INTO user_reports (reporter_id, target_type, target_id, reason, comment)
            VALUES (?, ?, ?, ?, ?)
            """,
            (reporter_id, target_type, target_id, reason, comment),
        )
        row = await db.fetch_one(
            "SELECT * FROM user_reports WHERE id = ?", (cursor.lastrowid,)
        )
        return cls.from_row(row)

    @classmethod
    async def exists(cls, reporter_id: int, target_type: str, target_id: int) -> bool:
        """Проверяет, жаловался ли пользователь на эту цель."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT id FROM user_reports WHERE reporter_id = ? AND target_type = ? AND target_id = ?",
            (reporter_id, target_type, target_id),
        )
        return row is not None

    @classmethod
    async def count_by_target(cls, target_type: str, target_id: int) -> int:
        """Подсчитывает жалобы на конкретную цель."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT COUNT(*) as count FROM user_reports WHERE target_type = ? AND target_id = ?",
            (target_type, target_id),
        )
        return row["count"] if row else 0
