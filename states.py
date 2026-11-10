from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    name = State()
    contact = State()


class ReviewForm(StatesGroup):
    rating = State()
    text = State()