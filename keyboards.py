from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def settings_keyboard(user_filters):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"📈 Мін. профіт: {user_filters['min_profit']}%", callback_data='change_min_profit'),
            InlineKeyboardButton(f"💰 Мін. обсяг: {user_filters['min_volume']} USDT", callback_data='change_min_volume')
        ],
        [
            InlineKeyboardButton(f"📊 Купівля: {user_filters['buy_exchange']}", callback_data='change_buy_exchange'),
            InlineKeyboardButton(f"💱 Продаж: {user_filters['sell_exchange']}", callback_data='change_sell_exchange')
        ],
        [
            InlineKeyboardButton(f"🔄 Ф’ючерси: {'✅' if user_filters['futures_enabled'] else '❌'}", callback_data='toggle_futures'),
            InlineKeyboardButton(f"⚙️ Арбітраж: {'✅' if user_filters['enabled'] else '❌'}", callback_data='toggle_enabled')
        ],
        [
            InlineKeyboardButton("🔽 Змінити фільтри", callback_data='change_filters')
        ]
    ])
