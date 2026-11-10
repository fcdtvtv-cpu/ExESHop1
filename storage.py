"""JSON-хранилище заказов и отзывов."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REVIEWS_FILE = DATA_DIR / "reviews.json"
ORDERS_FILE = DATA_DIR / "orders.json"


def _ensure_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not REVIEWS_FILE.exists():
        REVIEWS_FILE.write_text("[]", encoding="utf-8")
    if not ORDERS_FILE.exists():
        ORDERS_FILE.write_text("[]", encoding="utf-8")


def _read(path: Path) -> list[dict[str, Any]]:
    _ensure_files()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write(path: Path, data: list[dict[str, Any]]) -> None:
    _ensure_files()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def save_order(order: dict[str, Any]) -> dict[str, Any]:
    orders = _read(ORDERS_FILE)
    order["id"] = len(orders) + 1
    order["created_at"] = datetime.now().isoformat(timespec="seconds")
    order["status"] = "new"
    orders.append(order)
    _write(ORDERS_FILE, orders)
    return order


def get_order(order_id: int) -> dict[str, Any] | None:
    for o in _read(ORDERS_FILE):
        if o.get("id") == order_id:
            return o
    return None


def update_order_status(order_id: int, status: str) -> dict[str, Any] | None:
    orders = _read(ORDERS_FILE)
    for o in orders:
        if o.get("id") == order_id:
            o["status"] = status
            o["updated_at"] = datetime.now().isoformat(timespec="seconds")
            _write(ORDERS_FILE, orders)
            return o
    return None


def save_review(review: dict[str, Any]) -> dict[str, Any]:
    reviews = _read(REVIEWS_FILE)
    review["id"] = len(reviews) + 1
    review["created_at"] = datetime.now().isoformat(timespec="seconds")
    reviews.append(review)
    _write(REVIEWS_FILE, reviews)
    return review


def get_all_reviews() -> list[dict[str, Any]]:
    return _read(REVIEWS_FILE)


def get_reviews_stats() -> dict[str, Any]:
    reviews = get_all_reviews()
    if not reviews:
        return {"count": 0, "avg": 0.0}
    ratings = [r["rating"] for r in reviews if isinstance(r.get("rating"), (int, float))]
    avg = round(sum(ratings) / len(ratings), 1) if ratings else 0.0
    return {"count": len(reviews), "avg": avg}


def get_last_paid_order(user_id: int) -> dict[str, Any] | None:
    orders = _read(ORDERS_FILE)
    paid = [o for o in orders if o.get("user_id") == user_id and o.get("status") == "paid"]
    return paid[-1] if paid else None