import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from keyboards import main_menu_keyboard, filter_keyboard
from filters import init_user_filters, toggle_filter
from arbitrage import find_arbitrage_opportunities

import os
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()
TOKEN = os.getenv("TOKEN")  # Переконайся, що на Render назва змінної саме "TOKEN"

logging.basicConfig(level=logging.INFO)

# Словник для зберігання фільтрів користувачів
user_filters = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_filters[user_id] = init_user_filters()
    await update.message.reply_text("Привіт! 👋 Вибери дію:", reply_markup=main_menu_keyboard(user_filters[user_id]))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    data = query.data
    if data == "start_search":
        results = find_arbitrage_opportunities(user_filters[user_id])
        if results:
            for msg in results:
                await query.message.reply_text(msg, parse_mode="HTML")
        else:
            await query.message.reply_text("Арбітраж не знайдено за поточними фільтрами ❌")

    elif data == "filters":
        await query.message.reply_text("⚙️ Налаштуй фільтри:", reply_markup=filter_keyboard(user_filters[user_id]))

    elif data.startswith("filter_") or data.startswith("exchange_"):
        updated_filters = toggle_filter(user_id, data, user_filters[user_id])
        await query.message.edit_reply_markup(reply_markup=filter_keyboard(updated_filters))

# Головна точка входу
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        webhook_url=os.getenv("WEBHOOK_URL")
    )
