from aiogram import Router

from .start import router as start_router
from .catalog import router as catalog_router
from .order import router as order_router


def get_routers() -> list[Router]:
    return [start_router, catalog_router, order_router]