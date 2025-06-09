from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Клавіатура головного меню
def main_menu_keyboard(user_filters):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Шукати арбітраж", callback_data="start_search")],
        [InlineKeyboardButton("⚙️ Фільтри", callback_data="filters")]
    ])

# Клавіатура з фільтрами
def filter_keyboard(filters):
    buttons = []

    # Мін. профіт і обʼєм
    buttons.append([
        InlineKeyboardButton(f"Мін. профіт: {filters['min_profit']}%", callback_data="filter_profit"),
        InlineKeyboardButton(f"Мін. обсяг: {filters['min_volume']}$", callback_data="filter_volume")
    ])

    # Біржі купівлі
    buttons.append([InlineKeyboardButton("📥 Купівля на біржах:", callback_data="none")])
    for ex in filters['exchanges_buy']:
        state = "✅" if filters['exchanges_buy'][ex] else "❌"
        buttons.append([
            InlineKeyboardButton(f"{state} {ex}", callback_data=f"exchange_buy_{ex}")
        ])

    # Біржі продажу
    buttons.append([InlineKeyboardButton("📤 Продаж на біржах:", callback_data="none")])
    for ex in filters['exchanges_sell']:
        state = "✅" if filters['exchanges_sell'][ex] else "❌"
        buttons.append([
            InlineKeyboardButton(f"{state} {ex}", callback_data=f"exchange_sell_{ex}")
        ])

    return InlineKeyboardMarkup(buttons)
