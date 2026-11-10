from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Каталог товаров"), KeyboardButton(text="🛠 Заказать услугу")],
            [KeyboardButton(text="⚙️ Автоматизация"), KeyboardButton(text="🎮 Макросы")],
            [KeyboardButton(text="🔒 Безопасная сделка"), KeyboardButton(text="💬 Техподдержка")],
            [KeyboardButton(text="⭐ Отзывы"), KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел...",
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
    )


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()