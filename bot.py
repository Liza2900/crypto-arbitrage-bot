import logging
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from arbitrage import fetch_prices_from_exchanges, find_arbitrage_opportunities, EXCHANGES
from filters import get_user_filters, save_user_filters, settings_keyboard, exchanges_keyboard

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Натисніть кнопку нижче, щоб знайти арбітраж 👇", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Знайти арбітраж", callback_data="find_arbitrage")],
        [InlineKeyboardButton("⚙️ Налаштування", callback_data="settings")]
    ]))

async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    filters_data = get_user_filters(chat_id)

    if query.data == "find_arbitrage":
        await query.edit_message_text("⏳ Шукаю можливості арбітражу...")
        prices = await fetch_prices_from_exchanges(filters_data)
        opportunities = find_arbitrage_opportunities(prices, filters_data)
        if opportunities:
            text = "\n\n".join(opportunities)
        else:
            text = "❌ Арбітражних можливостей не знайдено за поточними фільтрами."
        await context.bot.send_message(chat_id, text)

    elif query.data == "settings":
        await query.edit_message_text("🔧 Налаштування:", reply_markup=settings_keyboard(filters_data))

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
        await query.edit_message_text("Увімкнені біржі:", reply_markup=exchanges_keyboard(filters_data["enabled_exchanges"]))

    elif query.data.startswith("toggle_exchange::"):
        exchange = query.data.split("::")[1]
        if exchange in filters_data["enabled_exchanges"]:
            filters_data["enabled_exchanges"].remove(exchange)
        else:
            filters_data["enabled_exchanges"].append(exchange)
        save_user_filters(chat_id, filters_data)
        await query.edit_message_reply_markup(reply_markup=exchanges_keyboard(filters_data["enabled_exchanges"]))

async def message_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    filters_data = get_user_filters(chat_id)
    text = update.message.text.strip()

    if context.user_data.get("awaiting_min_profit_usd"):
        try:
            filters_data["min_profit_usd"] = float(text)
            save_user_filters(chat_id, filters_data)
            await update.message.reply_text(f"✅ Мінімальний прибуток встановлено: {text} $", reply_markup=settings_keyboard(filters_data))
        except:
            await update.message.reply_text("❌ Некоректне значення. Спробуйте ще раз.")
        context.user_data["awaiting_min_profit_usd"] = False

    elif context.user_data.get("awaiting_budget"):
        try:
            filters_data["budget"] = float(text)
            save_user_filters(chat_id, filters_data)
            await update.message.reply_text(f"✅ Бюджет оновлено: {text} USDT", reply_markup=settings_keyboard(filters_data))
        except:
            await update.message.reply_text("❌ Некоректне значення. Спробуйте ще раз.")
        context.user_data["awaiting_budget"] = False

    elif context.user_data.get("awaiting_min_volume"):
        try:
            filters_data["min_volume_usdt"] = float(text)
            save_user_filters(chat_id, filters_data)
            await update.message.reply_text(f"✅ Мін. обсяг встановлено: {text} USDT", reply_markup=settings_keyboard(filters_data))
        except:
            await update.message.reply_text("❌ Некоректне значення. Спробуйте ще раз.")
        context.user_data["awaiting_min_volume"] = False

    elif context.user_data.get("awaiting_max_coin_price"):
        try:
            filters_data["max_coin_price"] = float(text)
            save_user_filters(chat_id, filters_data)
            await update.message.reply_text(f"✅ Макс. ціна монети: {text} $", reply_markup=settings_keyboard(filters_data))
        except:
            await update.message.reply_text("❌ Некоректне значення. Спробуйте ще раз.")
        context.user_data["awaiting_max_coin_price"] = False

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_webhook(listen="0.0.0.0", port=10000, webhook_url=WEBHOOK_URL)

if __name__ == "__main__":
    main()
