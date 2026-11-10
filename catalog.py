"""Просмотр игр, товаров, услуг, автоматизации, макросов."""

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.inline import (
    games_list_kb,
    game_products_kb,
    item_actions_kb,
    services_kb,
)
from bot.services.catalog import (
    GAME_TITLES,
    MACROS_GAME_TITLES,
    get_game_item,
    get_service,
    get_automation,
    get_macro_item,
)

router = Router(name="catalog")


# ---------- Каталог: игра -> товары ----------

@router.callback_query(F.data.startswith("cat_game:"))
async def cat_game(callback: CallbackQuery) -> None:
    game_id = callback.data.split(":")[1]
    title = GAME_TITLES.get(game_id, game_id)
    await callback.message.edit_text(
        f"<b>🛒 {title}</b>\n\nВыберите товар:",
        reply_markup=game_products_kb(game_id, "cat"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cat_item:"))
async def cat_item(callback: CallbackQuery) -> None:
    _, game_id, item_id = callback.data.split(":", 2)
    item = get_game_item(game_id, item_id)
    if not item:
        await callback.answer("Товар не найден", show_alert=True)
        return
    text = (
        f"<b>{item['title']}</b>\n\n"
        f"{item.get('description', '')}\n\n"
        f"💰 Цена: <b>{item.get('price', '—')}</b>"
    )
    await callback.message.edit_text(text, reply_markup=item_actions_kb(item_id))
    await callback.answer()


# ---------- Услуги ----------

@router.callback_query(F.data.startswith("svc:"))
async def show_service(callback: CallbackQuery) -> None:
    item_id = callback.data.split(":")[1]
    item = get_service(item_id)
    if not item:
        await callback.answer("Услуга не найдена", show_alert=True)
        return
    text = (
        f"<b>{item['title']}</b>\n\n"
        f"{item.get('description', '')}\n\n"
        f"💰 Цена: <b>{item.get('price', '—')}</b>"
    )
    await callback.message.edit_text(text, reply_markup=item_actions_kb(item_id))
    await callback.answer()


# ---------- Автоматизация ----------

@router.callback_query(F.data.startswith("auto:"))
async def show_automation(callback: CallbackQuery) -> None:
    item_id = callback.data.split(":")[1]
    item = get_automation(item_id)
    if not item:
        await callback.answer("Не найдено", show_alert=True)
        return
    pitch = item.get("pitch") or item.get("description", "")
    text = (
        f"<b>{item['title']}</b>\n\n"
        f"{pitch}\n\n"
        f"💰 Цена: <b>{item.get('price', '—')}</b>"
    )
    await callback.message.edit_text(text, reply_markup=item_actions_kb(item_id))
    await callback.answer()


# ---------- Макросы ----------

@router.callback_query(F.data.startswith("macro_game:"))
async def macro_game(callback: CallbackQuery) -> None:
    game_id = callback.data.split(":")[1]
    title = MACROS_GAME_TITLES.get(game_id, game_id)
    await callback.message.edit_text(
        f"<b>🎮 Макросы — {title}</b>\n\nВыберите вариант:",
        reply_markup=game_products_kb(game_id, "macro"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("macro_item:"))
async def macro_item(callback: CallbackQuery) -> None:
    _, game_id, item_id = callback.data.split(":", 2)
    item = get_macro_item(game_id, item_id)
    if not item:
        await callback.answer("Не найдено", show_alert=True)
        return
    text = (
        f"<b>{item['title']}</b>\n\n"
        f"{item.get('description', '')}\n\n"
        f"💰 Цена: <b>{item.get('price', '—')}</b>"
    )
    await callback.message.edit_text(text, reply_markup=item_actions_kb(item_id))
    await callback.answer()