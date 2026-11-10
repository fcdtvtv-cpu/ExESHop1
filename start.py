from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.config import settings
from bot.keyboards.reply import main_menu
from bot.keyboards.inline import (
    games_list_kb,
    services_kb,
    automation_kb,
    safe_platforms_kb,
    safe_platform_kb,
    support_kb,
)
from bot.services.catalog import get_platform
from bot.services.storage import get_all_reviews, get_reviews_stats

router = Router(name="start")


# ---------- /start ----------

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = (
        f"👋 Добро пожаловать в <b>{settings.shop_name}</b>!\n\n"
        "Здесь можно выбрать товар или услугу, оставить заявку "
        "и оформить безопасную сделку.\n\n"
        "Используйте меню ниже или команду /help"
    )
    await message.answer(text, reply_markup=main_menu())


# ---------- Навигация ----------

@router.callback_query(F.data == "nav:home")
async def nav_home(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer("Главное меню:", reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data == "nav:back")
async def nav_back(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Выберите раздел в меню ниже 👇"
    )
    await callback.message.answer("Главное меню:", reply_markup=main_menu())
    await callback.answer()


# ---------- Каталог ----------

@router.message(F.text == "🛒 Каталог товаров")
async def catalog_entry(message: Message) -> None:
    await message.answer(
        "<b>🛒 Каталог товаров</b>\n\n"
        "Выберите игру:",
        reply_markup=games_list_kb("cat"),
    )


@router.callback_query(F.data == "cat_games")
async def catalog_games(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "<b>🛒 Каталог товаров</b>\n\nВыберите игру:",
        reply_markup=games_list_kb("cat"),
    )
    await callback.answer()


# ---------- Заказать услугу ----------

@router.message(F.text == "🛠 Заказать услугу")
async def order_service_entry(message: Message) -> None:
    await message.answer(
        "<b>🛠 Заказать услугу</b>\n\n"
        "Выберите направление:\n"
        "• Игры — через каталог товаров\n"
        "• Услуги (AI, IT, хостинг и др.) — ниже",
        reply_markup=services_kb(),
    )


# ---------- Автоматизация ----------

@router.message(F.text == "⚙️ Автоматизация")
async def automation_entry(message: Message) -> None:
    await message.answer(
        "<b>⚙️ Автоматизация</b>\n\n"
        "Выберите направление:",
        reply_markup=automation_kb(),
    )


# ---------- Макросы ----------

@router.message(F.text == "🎮 Макросы")
async def macros_entry(message: Message) -> None:
    await message.answer(
        "<b>🎮 Макросы</b>\n\n"
        "Выберите игру:",
        reply_markup=games_list_kb("macro"),
    )


@router.callback_query(F.data == "macro_games")
async def macros_games(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "<b>🎮 Макросы</b>\n\nВыберите игру:",
        reply_markup=games_list_kb("macro"),
    )
    await callback.answer()


# ---------- Безопасная сделка ----------

@router.message(F.text == "🔒 Безопасная сделка")
@router.callback_query(F.data == "safe:list")
async def safe_deal_list(event: Message | CallbackQuery) -> None:
    text = (
        "<b>🔒 Безопасная сделка</b>\n\n"
        "Выберите площадку. Там есть гарант, отзывы и безопасная оплата.\n"
        "После перехода оформите заказ на сайте."
    )
    kb = safe_platforms_kb()
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb)
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("safe:") & ~F.data.in_({"safe:list"}))
async def safe_platform(callback: CallbackQuery) -> None:
    platform_id = callback.data.split(":")[1]
    platform = get_platform(platform_id)
    if not platform:
        await callback.answer("Площадка не найдена", show_alert=True)
        return
    text = (
        f"<b>🔒 {platform['title']}</b>\n\n"
        f"{platform.get('description', '')}\n\n"
        f"Профиль / товары:\n<code>{platform['url']}</code>\n\n"
        "Нажмите кнопку, чтобы перейти на площадку."
    )
    await callback.message.edit_text(text, reply_markup=safe_platform_kb(platform["url"]))
    await callback.answer()


# ---------- Техподдержка ----------

@router.message(F.text == "💬 Техподдержка")
async def support(message: Message) -> None:
    username = settings.support_username.lstrip("@")
    text = (
        "<b>💬 Техподдержка</b>\n\n"
        "Напишите напрямую продавцу — ответим как можно скорее.\n\n"
        f"Профиль: @{username}"
    )
    await message.answer(text, reply_markup=support_kb(username))


# ---------- Отзывы ----------

@router.message(F.text == "⭐ Отзывы")
async def show_reviews(message: Message) -> None:
    stats = get_reviews_stats()
    reviews = get_all_reviews()

    if not reviews:
        await message.answer(
            "<b>⭐ Отзывы</b>\n\n"
            "Пока нет завершённых сделок с отзывами.\n"
            "Будьте первым!",
            reply_markup=main_menu(),
        )
        return

    stars = "⭐" * int(round(stats["avg"])) if stats["avg"] else "—"
    header = (
        f"<b>⭐ Отзывы покупателей</b>\n"
        f"Средняя оценка: <b>{stats['avg']}</b> {stars} "
        f"({stats['count']} шт.)\n"
        f"{'─' * 24}\n"
    )
    lines = []
    for r in reversed(reviews[-10:]):
        rating = int(r.get("rating", 0))
        text = r.get("text") or "без комментария"
        name = r.get("name") or "Покупатель"
        product = r.get("product_title") or "услуга"
        lines.append(
            f"{'⭐' * rating}{'☆' * (5 - rating)}  <b>{name}</b>\n"
            f"<i>{product}</i>\n"
            f"{text}"
        )
    await message.answer(header + "\n\n".join(lines), reply_markup=main_menu())


# ---------- /help и Помощь ----------

HELP_TEXT = """
<b>ℹ️ Справка по боту</b>

<b>🛒 Каталог товаров</b>
Игры → выбор игры → товар → цена.
Можно оставить заявку или перейти к безопасной сделке.

<b>🛠 Заказать услугу</b>
AI, IT-разработка, хостинг, дизайн и другие услуги.
После выбора — заявка продавцу.

<b>⚙️ Автоматизация</b>
Готовые решения:
• Парсинг данных
• Excel / Google Таблицы
• Сборщик заявок в Telegram
• Мониторинг цен и сайтов
• Автопостинг
• Автоответчик с ИИ

<b>🎮 Макросы</b>
Макросы под игры. Выберите игру и вариант.

<b>🔒 Безопасная сделка</b>
Сделка через площадку (Playerok, Kwork, GGSale, FunPay).
Гарант, отзывы, безопасная оплата. Выберите площадку и перейдите по ссылке.

<b>💬 Техподдержка</b>
Прямая связь с продавцом в Telegram.

<b>⭐ Отзывы</b>
Оценки и комментарии покупателей после завершённых сделок.

<b>Как проходит сделка по заявке</b>
1. Вы оставляете заявку (товар, имя, контакт).
2. Продавец получает её в личные сообщения.
3. Продавец пишет вам, обсуждаете детали и оплату.
4. После оплаты продавец отмечает сделку — вам придёт запрос отзыва.

<b>Как проходит безопасная сделка</b>
1. Выбираете площадку в разделе «Безопасная сделка».
2. Переходите на сайт, оформляете заказ там.
3. Оплата и гарантии — через площадку.

Команды: /start — меню, /help — эта справка.
""".strip()


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu())