import os
import json
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

FILTERS_FILE = "user_filters.json"

DEFAULT_FILTERS = {
    "budget": 100,
    "min_profit_usd": 1.0,
    "min_volume_usdt": 10.0,
    "max_coin_price": 15.0,
    "enabled_exchanges": ["KuCoin", "MEXC", "Bitget", "OKX", "BingX", "Gate.io", "CoinEx"]
}

def get_user_filters(chat_id):
    if not os.path.exists(FILTERS_FILE):
        return DEFAULT_FILTERS.copy()

    try:
        with open(FILTERS_FILE, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return DEFAULT_FILTERS.copy()

    user_filters = data.get(str(chat_id), {})
    full_filters = DEFAULT_FILTERS.copy()
    full_filters.update(user_filters)
    return full_filters

def save_user_filters(chat_id, filters):
    data = {}
    if os.path.exists(FILTERS_FILE):
        try:
            with open(FILTERS_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    data[str(chat_id)] = filters
    with open(FILTERS_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def settings_keyboard(filters):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💰 Бюджет: {filters['budget']} USDT", callback_data="change_budget")],
        [InlineKeyboardButton(f"📊 Мін. прибуток: {filters['min_profit_usd']} $", callback_data="change_min_profit_usd")],
        [InlineKeyboardButton(f"📦 Мін. обсяг: {filters['min_volume_usdt']} USDT", callback_data="change_min_volume")],
        [InlineKeyboardButton(f"💎 Макс. ціна монети: {filters['max_coin_price']} $", callback_data="change_max_coin_price")],
        [InlineKeyboardButton("⚙️ Увімкнені біржі", callback_data="toggle_exchanges")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="start")]
    ])

def exchanges_keyboard(current_exchanges):
    rows = []
    for exchange in DEFAULT_FILTERS["enabled_exchanges"]:
        status = "✅" if exchange in current_exchanges else "❌"
        rows.append([InlineKeyboardButton(f"{status} {exchange}", callback_data=f"toggle_{exchange}")])
    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="settings")])
    return InlineKeyboardMarkup(rows)
