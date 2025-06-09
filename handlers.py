from telegram import Update
from telegram.ext import CallbackContext
from keyboards import main_menu_keyboard, filter_keyboard
from filters_config import user_filters
from arbitrage import generate_arbitrage_signals

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in user_filters:
        user_filters[user_id] = {
            "min_profit": 0.8,
            "min_volume": 10,
            "exchanges_buy": {"KuCoin": True, "MEXC": True, "OKX": True, "Bitget": True, "BingX": True, "Gate.io": True, "Bybit": True},
            "exchanges_sell": {"KuCoin": True, "MEXC": True, "OKX": True, "Bitget": True, "BingX": True, "Gate.io": True, "Bybit": True}
        }
    update.message.reply_text("👋 Вітаю! Обери дію:", reply_markup=main_menu_keyboard(user_filters[user_id]))

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    data = query.data
    filters = user_filters.get(user_id)

    if data == "start_search":
        signals = generate_arbitrage_signals(filters)
        if signals:
            for signal in signals:
                query.message.reply_text(signal, parse_mode="HTML", disable_web_page_preview=True)
        else:
            query.message.reply_text("😕 Немає арбітражних можливостей за вашими фільтрами.")

    elif data == "filters":
        query.message.reply_text("⚙️ Налаштування фільтрів:", reply_markup=filter_keyboard(filters))

    elif data.startswith("filter_profit"):
        filters['min_profit'] += 0.1
        query.edit_message_reply_markup(reply_markup=filter_keyboard(filters))

    elif data.startswith("filter_volume"):
        filters['min_volume'] += 10
        query.edit_message_reply_markup(reply_markup=filter_keyboard(filters))

    elif data.startswith("exchange_buy_"):
        ex = data.split("exchange_buy_")[1]
        filters['exchanges_buy'][ex] = not filters['exchanges_buy'][ex]
        query.edit_message_reply_markup(reply_markup=filter_keyboard(filters))

    elif data.startswith("exchange_sell_"):
        ex = data.split("exchange_sell_")[1]
        filters['exchanges_sell'][ex] = not filters['exchanges_sell'][ex]
        query.edit_message_reply_markup(reply_markup=filter_keyboard(filters))
