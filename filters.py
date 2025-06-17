from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

FILTERS_FILE = "user_filters.json"

def get_user_filters(chat_id):
    if not os.path.exists(FILTERS_FILE):
        return {
            "budget": 100,
            "min_profit_usd": 1.0
        }
    with open(FILTERS_FILE, "r") as f:
        data = json.load(f)
    return data.get(str(chat_id), {
        "budget": 100,
        "min_profit_usd": 1.0
    })

def save_user_filters(chat_id, filters):
    data = {}
    if os.path.exists(FILTERS_FILE):
        with open(FILTERS_FILE, "r") as f:
            data = json.load(f)
    data[str(chat_id)] = filters
    with open(FILTERS_FILE, "w") as f:
        json.dump(data, f)

def settings_keyboard(filters):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💰 Бюджет: {filters['budget']} USDT", callback_data="change_budget")],
        [InlineKeyboardButton(f"📊 Мін. прибуток: {filters['min_profit_usd']} $", callback_data="change_min_profit_usd")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="start")]
    ])
