# filters.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

EXCHANGES = ["KuCoin", "MEXC", "Bitget", "OKX", "BingX", "Gate.io", "Bybit"]

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

def build_exchange_toggle_menu(filters, mode):
    exchanges = filters[f'exchanges_{mode}']
    rows = [
        [InlineKeyboardButton(f"{'✅' if enabled else '❌'} {ex}", callback_data=f"toggle_{mode}_{ex}")]
        for ex, enabled in exchanges.items()
    ]
    rows.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_filters")])
    return InlineKeyboardMarkup(rows)

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
        await query.edit_message_text(
            "⚙️ Увімкніть/вимкніть біржі для **купівлі**:",
            reply_markup=build_exchange_toggle_menu(filters, "buy"),
            parse_mode="Markdown"
        )
        return
    elif data == "edit_exchanges_sell":
        await query.edit_message_text(
            "⚙️ Увімкніть/вимкніть біржі для **продажу**:",
            reply_markup=build_exchange_toggle_menu(filters, "sell"),
            parse_mode="Markdown"
        )
        return
    elif data == "back_to_filters":
        await query.edit_message_text(
            "⬇️ Меню фільтрів:",
            reply_markup=build_filters_menu(filters)
        )
        return
    else:
        # toggle_exchange_buy_KuCoin
        if data.startswith("toggle_buy_"):
            ex = data.replace("toggle_buy_", "")
            filters['exchanges_buy'][ex] = not filters['exchanges_buy'][ex]
            await query.edit_message_reply_markup(
                reply_markup=build_exchange_toggle_menu(filters, "buy")
            )
            context.user_data['filters'] = filters
            return
        elif data.startswith("toggle_sell_"):
            ex = data.replace("toggle_sell_", "")
            filters['exchanges_sell'][ex] = not filters['exchanges_sell'][ex]
            await query.edit_message_reply_markup(
                reply_markup=build_exchange_toggle_menu(filters, "sell")
            )
            context.user_data['filters'] = filters
            return

    context.user_data['filters'] = filters
    await query.edit_message_reply_markup(reply_markup=build_filters_menu(filters))
