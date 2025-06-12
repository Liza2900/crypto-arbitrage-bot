from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from arbitrage import EXCHANGES

def build_filters_menu(filters):
    buttons = [
        [InlineKeyboardButton(f"💰 Мін. профіт: {filters['min_profit']}%", callback_data="set_min_profit")],
        [InlineKeyboardButton(f"📦 Мін. обсяг: {filters['min_volume']}$", callback_data="set_min_volume")],
        [InlineKeyboardButton(f"💼 Бюджет: {filters['budget']}$", callback_data="set_budget")],
        [InlineKeyboardButton(f"📈 Ф’ючерси: {'Так' if filters['is_futures'] else 'Ні'}", callback_data="toggle_futures")],
        [InlineKeyboardButton("🔁 Біржі покупки", callback_data="edit_exchanges_buy")],
        [InlineKeyboardButton("🔁 Біржі продажу", callback_data="edit_exchanges_sell")],
        [InlineKeyboardButton(f"⏱ Макс. час життя: {filters['max_lifetime']}с", callback_data="set_max_lifetime")]
    ]
    return InlineKeyboardMarkup(buttons)

async def handle_filter_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    filters = context.user_data.get('filters', {})
    if not filters:
        filters = {
            'min_profit': 0.8,
            'min_volume': 10,
            'budget': 100,
            'is_futures': False,
            'exchanges_buy': {ex: True for ex in EXCHANGES},
            'exchanges_sell': {ex: True for ex in EXCHANGES},
            'max_lifetime': 30
        }

    if data == "toggle_futures":
        filters['is_futures'] = not filters['is_futures']
    elif data == "set_min_profit":
        filters['min_profit'] = round(filters['min_profit'] + 0.1, 1)
    elif data == "set_min_volume":
        filters['min_volume'] += 10
    elif data == "set_budget":
        filters['budget'] += 50
    elif data == "set_max_lifetime":
        filters['max_lifetime'] += 10
    elif data == "edit_exchanges_buy":
        await query.edit_message_text("⚙️ Налаштування бірж купівлі: (не реалізовано)")
        return
    elif data == "edit_exchanges_sell":
        await query.edit_message_text("⚙️ Налаштування бірж продажу: (не реалізовано)")
        return

    context.user_data['filters'] = filters
    await query.edit_message_reply_markup(reply_markup=build_filters_menu(filters))
