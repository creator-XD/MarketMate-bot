# Быстрый старт

Краткая инструкция по запуску Telegram Marketplace Bot в локальном окружении.

## 1. Подготовьте окружение

Установите Python 3.11 или новее и создайте виртуальное окружение:

```bash
python -m venv venv
```

Активация на Windows:

```bash
venv\Scripts\activate
```

Активация на Linux/macOS:

```bash
source venv/bin/activate
```

## 2. Установите зависимости

```bash
pip install -r requirements.txt
```

## 3. Создайте `.env`

Скопируйте пример конфигурации и заполните значения:

```bash
copy .env.example .env
```

Минимально нужны:

```env
BOT_TOKEN=ваш_токен_от_BotFather
ADMIN_TELEGRAM_IDS=123456789
SUPER_ADMIN_ID=123456789
```

## 4. Запустите бота

```bash
python bot.py
```

При первом запуске SQLite-база `marketplace.db` и нужные таблицы создаются автоматически.

## 5. Создайте администратора

Сначала администратор должен отправить `/start` боту, чтобы его пользователь появился в базе. Затем выполните:

```bash
python scripts/create_admin.py
```

Для проверки настройки можно запустить:

```bash
python scripts/check_admin_setup.py
```

## 6. Проверьте сценарии

- `/start` открывает главное меню.
- `/mylistings` позволяет создать объявление.
- `/search` открывает поиск и фильтры.
- `/admin` открывает админ-панель для разрешённых Telegram ID.
