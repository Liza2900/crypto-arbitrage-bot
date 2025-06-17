from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from filters import user_filters

EXCHANGES = ["KuCoin", "MEXC", "OKX", "Bitget", "BingX", "Gate", "CoinEx"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_filters:
        user_filters[user_id] = {
            "min_profit": 0.8,
            "min_volume": 10,
            "buy_exchanges": [],
            "sell_exchanges": [],
            "futures": False,
            "search_enabled": True,
            "budget": 100,
        }
    await update.message.reply_text("Привіт! Обери, що хочеш налаштувати:", reply_markup=main_menu_keyboard())

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Увімкнути/вимкнути пошук", callback_data="toggle_search")],
        [InlineKeyboardButton("📈 Мін. профіт", callback_data="set_min_profit"),
         InlineKeyboardButton("💰 Мін. обсяг", callback_data="set_min_volume")],
        [InlineKeyboardButton("🏦 Біржі покупки", callback_data="select_buy_exchanges"),
         InlineKeyboardButton("🏪 Біржі продажу", callback_data="select_sell_exchanges")],
        [InlineKeyboardButton("📊 Увімкнути/вимкнути ф’ючерси", callback_data="toggle_futures")],
        [InlineKeyboardButton("💼 Бюджет", callback_data="set_budget")],
        [InlineKeyboardButton("✅ Запустити пошук", callback_data="start_search")]
    ])

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "toggle_search":
        user_filters[user_id]["search_enabled"] = not user_filters[user_id]["search_enabled"]
        status = "увімкнено" if user_filters[user_id]["search_enabled"] else "вимкнено"
        await query.edit_message_text(f"Пошук {status}.", reply_markup=main_menu_keyboard())

    elif query.data == "toggle_futures":
        user_filters[user_id]["futures"] = not user_filters[user_id]["futures"]
        status = "увімкнено" if user_filters[user_id]["futures"] else "вимкнено"
        await query.edit_message_text(f"Ф’ючерси {status}.", reply_markup=main_menu_keyboard())

    elif query.data == "set_min_profit":
        await query.edit_message_text("Введи мінімальний профіт у %:")
        context.user_data["setting"] = "min_profit"

    elif query.data == "set_min_volume":
        await query.edit_message_text("Введи мінімальний обсяг у USDT:")
        context.user_data["setting"] = "min_volume"

    elif query.data == "set_budget":
        await query.edit_message_text("Введи свій бюджет у USDT:")
        context.user_data["setting"] = "budget"

    elif query.data == "select_buy_exchanges":
        await show_exchange_selection(update, context, "buy_exchanges")

    elif query.data == "select_sell_exchanges":
        await show_exchange_selection(update, context, "sell_exchanges")

    elif query.data == "start_search":
        await query.edit_message_text("Пошук арбітражу запущено. Очікуйте результати…")
        # тут має бути логіка запуску пошуку

async def show_exchange_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, exchange_type: str):
    user_id = update.callback_query.from_user.id
    selected = user_filters[user_id].get(exchange_type, [])

    keyboard = []
    for ex in EXCHANGES:
        selected_symbol = "✅ " if ex in selected else ""
        keyboard.append([
            InlineKeyboardButton(f"{selected_symbol}{ex}", callback_data=f"toggle_{exchange_type}_{ex}")
        ])

    keyboard.append([InlineKeyboardButton("⬅ Назад", callback_data="back_to_menu")])
    await update.callback_query.edit_message_text(
        f"Оберіть біржі для {'купівлі' if exchange_type == 'buy_exchanges' else 'продажу'}:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_exchange_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data.startswith("toggle_buy_exchanges_"):
        exchange = query.data.replace("toggle_buy_exchanges_", "")
        toggle_exchange(user_id, "buy_exchanges", exchange)
        await show_exchange_selection(update, context, "buy_exchanges")

    elif query.data.startswith("toggle_sell_exchanges_"):
        exchange = query.data.replace("toggle_sell_exchanges_", "")
        toggle_exchange(user_id, "sell_exchanges", exchange)
        await show_exchange_selection(update, context, "sell_exchanges")

    elif query.data == "back_to_menu":
        await query.edit_message_text("Повернення до головного меню:", reply_markup=main_menu_keyboard())

def toggle_exchange(user_id: int, key: str, exchange: str):
    exchanges = user_filters[user_id].get(key, [])
    if exchange in exchanges:
        exchanges.remove(exchange)
    else:
        exchanges.append(exchange)
    user_filters[user_id][key] = exchanges

