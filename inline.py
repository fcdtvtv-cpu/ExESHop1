from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.catalog import (
    GAMES,
    GAME_TITLES,
    SERVICES,
    AUTOMATION,
    MACROS_GAMES,
    MACROS_GAME_TITLES,
    SAFE_PLATFORMS,
)
from bot.config import settings


# ---------- Каталог: игры ----------

def games_list_kb(prefix: str = "cat") -> InlineKeyboardMarkup:
    """prefix: cat | order | macro"""
    builder = InlineKeyboardBuilder()
    titles = MACROS_GAME_TITLES if prefix == "macro" else GAME_TITLES
    source = MACROS_GAMES if prefix == "macro" else GAMES
    for game_id in source:
        title = titles.get(game_id, game_id)
        builder.row(
            InlineKeyboardButton(text=title, callback_data=f"{prefix}_game:{game_id}")
        )
    builder.row(InlineKeyboardButton(text="« Назад", callback_data="nav:home"))
    return builder.as_markup()


def game_products_kb(game_id: str, prefix: str = "cat") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    source = MACROS_GAMES if prefix == "macro" else GAMES
    for item in source.get(game_id, []):
        builder.row(
            InlineKeyboardButton(
                text=f"{item['title']} · {item.get('price', '—')}",
                callback_data=f"{prefix}_item:{game_id}:{item['id']}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="« К играм", callback_data=f"{prefix}_games")
    )
    return builder.as_markup()


def item_actions_kb(item_id: str, show_safe: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 Оставить заявку", callback_data=f"order:{item_id}")
    )
    if show_safe:
        builder.row(
            InlineKeyboardButton(text="🔒 Безопасная сделка", callback_data="safe:list")
        )
    builder.row(InlineKeyboardButton(text="« Назад", callback_data="nav:back"))
    return builder.as_markup()


# ---------- Услуги ----------

def services_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in SERVICES:
        builder.row(
            InlineKeyboardButton(
                text=item["title"],
                callback_data=f"svc:{item['id']}",
            )
        )
    builder.row(InlineKeyboardButton(text="« Назад", callback_data="nav:home"))
    return builder.as_markup()


# ---------- Автоматизация ----------

def automation_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in AUTOMATION:
        builder.row(
            InlineKeyboardButton(
                text=item["title"],
                callback_data=f"auto:{item['id']}",
            )
        )
    builder.row(InlineKeyboardButton(text="« Назад", callback_data="nav:home"))
    return builder.as_markup()


# ---------- Безопасная сделка ----------

def safe_platforms_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in SAFE_PLATFORMS:
        builder.row(
            InlineKeyboardButton(
                text=p["title"],
                callback_data=f"safe:{p['id']}",
            )
        )
    builder.row(InlineKeyboardButton(text="« В меню", callback_data="nav:home"))
    return builder.as_markup()


def safe_platform_kb(url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🌐 Перейти на площадку", url=url))
    builder.row(InlineKeyboardButton(text="« К площадкам", callback_data="safe:list"))
    builder.row(InlineKeyboardButton(text="« В меню", callback_data="nav:home"))
    return builder.as_markup()


# ---------- Заявка / админ / отзывы ----------

def admin_order_kb(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Клиент оплатил товар",
            callback_data=f"paid:{order_id}",
        )
    )
    return builder.as_markup()


def rating_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text=str(i), callback_data=f"rate:{i}")
        for i in range(6)
    ]
    builder.row(*buttons)
    return builder.as_markup()


def skip_review_text_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Пропустить", callback_data="review:skip_text")
    )
    return builder.as_markup()


def support_kb(username: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="💬 Написать в поддержку",
            url=f"https://t.me/{username.lstrip('@')}",
        )
    )
    builder.row(InlineKeyboardButton(text="« В меню", callback_data="nav:home"))
    return builder.as_markup()