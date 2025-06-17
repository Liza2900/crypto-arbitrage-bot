from telegram import Update
from telegram.ext import CallbackContext
from filters import get_user_filters, save_user_filters, settings_keyboard, exchanges_keyboard

async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    filters = get_user_filters(chat_id)

    if query.data == "find_arbitrage":
        await query.edit_message_text("⏳ Шукаю можливості арбітражу...")
        from arbitrage import fetch_prices_from_exchanges, find_arbitrage_opportunities
        prices = await fetch_prices_from_exchanges(filters)
        opportunities = find_arbitrage_opportunities(prices, filters)
        if opportunities:
            text = "\n\n".join(opportunities)
        else:
            text = "❌ Арбітражних можливостей не знайдено за поточними фільтрами."
        await context.bot.send_message(chat_id, text)

    elif query.data == "settings":
        await query.edit_message_text("🔧 Налаштування:", reply_markup=settings_keyboard(filters))

    elif query.data == "change_min_profit_usd":
        await context.bot.send_message(chat_id, "Введіть мінімальний прибуток у $ (наприклад, 2):")
        context.user_data["awaiting_min_profit_usd"] = True

    elif query.data == "change_budget":
        await context.bot.send_message(chat_id, "Введіть бюджет у USDT (наприклад, 100):")
        context.user_data["awaiting_budget"] = True

    elif query.data == "change_min_volume":
        await context.bot.send_message(chat_id, "Введіть мінімальний обсяг угоди в USDT (наприклад, 10):")
        context.user_data["awaiting_min_volume"] = True

    elif query.data == "change_max_coin_price":
        await context.bot.send_message(chat_id, "Введіть максимальну ціну монети в $ (наприклад, 15):")
        context.user_data["awaiting_max_coin_price"] = True

    elif query.data == "toggle_exchanges":
        await query.edit_message_text("🟢 Увімкнені біржі:", reply_markup=exchanges_keyboard(filters["enabled_exchanges"]))

    elif query.data.startswith("toggle_exchange::"):
        exchange = query.data.split("::")[1]
        enabled = filters["enabled_exchanges"]
        if exchange in enabled:
            enabled.remove(exchange)
        else:
            enabled.append(exchange)
        save_user_filters(chat_id, filters)
        await query.edit_message_text("🟢 Оновлено список бірж:", reply_markup=exchanges_keyboard(filters["enabled_exchanges"]))

async def message_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    filters = get_user_filters(chat_id)

    if context.user_data.get("awaiting_min_profit_usd"):
        try:
            min_profit = float(update.message.text.strip())
            filters["min_profit_usd"] = min_profit
            await update.message.reply_text(f"✅ Мінімальний прибуток встановлено: {min_profit} $", reply_markup=settings_keyboard(filters))
        except:
            await update.message.reply_text("❌ Некоректне значення. Спробуйте ще раз.")
        context.user_data["awaiting_min_profit_usd"] = False

    elif context.user_data.get("awaiting_budget"):
        try:
            budget = float(update.message.text.strip())
            filters["budget"] = budget
            await update.message.reply_text(f"✅ Бюджет встановлено: {budget} USDT", reply_markup=settings_keyboard(filters))
        except:
            await update.message.reply_text("❌ Некоректне значення. Спробуйте ще раз.")
        context.user_data["awaiting_budget"] = False

    elif context.user_data.get("awaiting_min_volume"):
        try:
            min_vol = float(update.message.text.strip())
            filters["min_volume_usdt"] = min_vol
            await update.message.reply_text(f"✅ Мінімальний обсяг встановлено: {min_vol} USDT", reply_markup=settings_keyboard(filters))
        except:
            await update.message.reply_text("❌ Некоректне значення. Спробуйте ще раз.")
        context.user_data["awaiting_min_volume"] = False

    elif context.user_data.get("awaiting_max_coin_price"):
        try:
            max_price = float(update.message.text.strip())
            filters["max_coin_price"] = max_price
            await update.message.reply_text(f"✅ Максимальна ціна монети встановлена: {max_price} $", reply_markup=settings_keyboard(filters))
        except:
            await update.message.reply_text("❌ Некоректне значення. Спробуйте ще раз.")
        context.user_data["awaiting_max_coin_price"] = False

    save_user_filters(chat_id, filters)

