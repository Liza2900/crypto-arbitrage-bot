import logging
import os
from fastapi import FastAPI
import uvicorn

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from keyboards import main_menu_keyboard, filter_keyboard
from filters import init_user_filters, toggle_filter
from arbitrage import find_arbitrage_opportunities

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

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

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"status": "OK"}

if __name__ == "__main__":
    from telegram.ext import Application

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))

    # Запускаємо Telegram бота
    import asyncio

    async def main():
        # Запускаємо бот і FastAPI одночасно
        import threading

        # Запуск FastAPI у фоновому потоці
        def start_api():
            uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

        api_thread = threading.Thread(target=start_api, daemon=True)
        api_thread.start()

        # Запуск Telegram бота з вебхуком
        await application.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT", 8080)),
            webhook_url=os.getenv("WEBHOOK_URL")
        )

    asyncio.run(main())
