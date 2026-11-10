"""Заявки, оплата, отзывы."""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.config import settings
from bot.states import OrderForm, ReviewForm
from bot.keyboards.reply import main_menu, cancel_kb
from bot.keyboards.inline import admin_order_kb, rating_kb, skip_review_text_kb
from bot.services.catalog import find_item_title
from bot.services.storage import (
    save_order,
    get_order,
    update_order_status,
    save_review,
    get_last_paid_order,
)

router = Router(name="order")


# ---------- Старт заявки ----------

@router.callback_query(F.data.startswith("order:"))
async def start_order(callback: CallbackQuery, state: FSMContext) -> None:
    item_id = callback.data.split(":", 1)[1]
    title = find_item_title(item_id)

    await state.clear()
    await state.update_data(product_id=item_id, product_title=title)
    await state.set_state(OrderForm.name)

    await callback.message.edit_text(
        f"Вы выбрали: <b>{title}</b>\n\n"
        "<b>Шаг 1/2</b>\n"
        "Как вас зовут?"
    )
    await callback.message.answer(
        "Введите имя или нажмите «Отмена»:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(OrderForm.name, F.text == "❌ Отмена")
@router.message(OrderForm.contact, F.text == "❌ Отмена")
async def cancel_order(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Заявка отменена.", reply_markup=main_menu())


@router.message(OrderForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Введите корректное имя (минимум 2 символа).")
        return
    await state.update_data(name=name)
    await state.set_state(OrderForm.contact)
    await message.answer(
        f"Приятно познакомиться, <b>{name}</b>!\n\n"
        "<b>Шаг 2/2</b>\n"
        "Укажите удобный способ связи:\n"
        "• Telegram (@username)\n"
        "• Телефон\n"
        "• Email",
        reply_markup=cancel_kb(),
    )


@router.message(OrderForm.contact)
async def process_contact(message: Message, state: FSMContext, bot: Bot) -> None:
    contact = (message.text or "").strip()
    if len(contact) < 3:
        await message.answer("Укажите корректный контакт.")
        return

    data = await state.get_data()
    await state.clear()

    order = save_order({
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "full_name": message.from_user.full_name,
        "name": data["name"],
        "contact": contact,
        "product_id": data["product_id"],
        "product_title": data["product_title"],
    })

    await message.answer(
        "✅ <b>Заявка отправлена!</b>\n\n"
        "Продавец скоро ответит, ожидайте.",
        reply_markup=main_menu(),
    )

    username = f"@{message.from_user.username}" if message.from_user.username else "нет"
    admin_text = (
        f"<b>📋 Новая заявка #{order['id']}</b>\n"
        f"{'─' * 24}\n"
        f"<b>Товар / услуга:</b> {data['product_title']}\n"
        f"<b>Имя:</b> {data['name']}\n"
        f"<b>Контакт:</b> {contact}\n"
        f"{'─' * 24}\n"
        f"<b>От:</b> {message.from_user.full_name} ({username})\n"
        f"<b>ID:</b> <code>{message.from_user.id}</code>"
    )
    try:
        await bot.send_message(
            chat_id=settings.admin_id,
            text=admin_text,
            reply_markup=admin_order_kb(order["id"]),
        )
    except Exception:
        pass


# ---------- Продавец: клиент оплатил ----------

@router.callback_query(F.data.startswith("paid:"))
async def mark_paid(callback: CallbackQuery, bot: Bot) -> None:
    if callback.from_user.id != settings.admin_id:
        await callback.answer("Только для продавца", show_alert=True)
        return

    order_id = int(callback.data.split(":")[1])
    order = get_order(order_id)
    if not order:
        await callback.answer("Заявка не найдена", show_alert=True)
        return
    if order.get("status") == "paid":
        await callback.answer("Уже отмечено", show_alert=True)
        return

    update_order_status(order_id, "paid")

    original = callback.message.html_text or callback.message.text or ""
    await callback.message.edit_text(
        original + "\n\n✅ <b>Клиент оплатил</b>",
        reply_markup=None,
    )
    await callback.answer("Статус обновлён")

    try:
        await bot.send_message(
            chat_id=order["user_id"],
            text=(
                "🎉 Сделка завершена!\n\n"
                "<b>Оставьте отзыв, как прошла сделка?</b>\n"
                "Оцените от 0 до 5:"
            ),
            reply_markup=rating_kb(),
        )
    except Exception:
        pass


# ---------- Оценка ----------

@router.callback_query(F.data.startswith("rate:"))
async def process_rating(callback: CallbackQuery, state: FSMContext) -> None:
    rating = int(callback.data.split(":")[1])
    if rating < 0 or rating > 5:
        await callback.answer("Некорректная оценка")
        return
    await state.update_data(rating=rating)
    await state.set_state(ReviewForm.text)
    await callback.message.edit_text(
        f"Вы поставили: <b>{rating}/5</b>\n\n"
        "Напишите короткий комментарий (или «Пропустить»):",
        reply_markup=skip_review_text_kb(),
    )
    await callback.answer()


@router.callback_query(ReviewForm.text, F.data == "review:skip_text")
async def skip_review_text(callback: CallbackQuery, state: FSMContext) -> None:
    await _save_review(callback.from_user, state, text=None)
    await callback.message.edit_text(
        "Спасибо за отзыв! 🙏\nОн появится в разделе «⭐ Отзывы»."
    )
    await callback.message.answer("Главное меню:", reply_markup=main_menu())
    await callback.answer()


@router.message(ReviewForm.text)
async def process_review_text(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    await _save_review(message.from_user, state, text=text)
    await message.answer(
        "Спасибо за отзыв! 🙏\nОн появится в разделе «⭐ Отзывы».",
        reply_markup=main_menu(),
    )


async def _save_review(user, state: FSMContext, text: str | None) -> None:
    data = await state.get_data()
    rating = data.get("rating", 0)
    await state.clear()
    order = get_last_paid_order(user.id) or {}
    save_review({
        "user_id": user.id,
        "name": order.get("name") or user.full_name,
        "rating": rating,
        "text": text,
        "product_title": order.get("product_title"),
        "order_id": order.get("id"),
    })
    if order.get("id"):
        update_order_status(order["id"], "reviewed")