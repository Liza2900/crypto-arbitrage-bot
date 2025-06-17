import logging
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from arbitrage import fetch_prices_from_exchanges, find_arbitrage_opportunities, EXCHANGES
from filters import get_user_filters, save_user_filters, settings_keyboard

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
    filters = get_user_filters(chat_id)

    if query.data == "find_arbitrage":
        await query.edit_message_text("⏳ Шукаю можливості арбітражу...")
        prices = await fetch_prices_from_exchanges(filters)
        opportunities = find_arbitrage_opportunities(prices, filters)
        if opportunities:
            text = "

".join(opportunities)
        else:
            text = "❌ Арбітражних можливостей не знайдено за поточними фільтрами."
        await context.bot.send_message(chat_id, text)

    elif query.data == "settings":
        await query.edit_message_text("🔧 Налаштування:", reply_markup=settings_keyboard(filters))

    elif query.data == "change_min_profit_usd":
        await context.bot.send_message(chat_id, "Введіть мінімальний прибуток у $ (наприклад, 2):")
        context.user_data["awaiting_min_profit_usd"] = True

async def message_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if context.user_data.get("awaiting_min_profit_usd"):
        try:
            min_profit = float(update.message.text.strip())
            filters = get_user_filters(chat_id)
            filters["min_profit_usd"] = min_profit
            save_user_filters(chat_id, filters)
            await context.bot.send_message(chat_id, f"✅ Мінімальний прибуток встановлено: {min_profit} $", reply_markup=settings_keyboard(filters))
        except:
            await context.bot.send_message(chat_id, "❌ Некоректне значення. Спробуйте ще раз.")
        context.user_data["awaiting_min_profit_usd"] = False

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_webhook(listen="0.0.0.0", port=10000, webhook_url=WEBHOOK_URL)

if __name__ == "__main__":
    main()
