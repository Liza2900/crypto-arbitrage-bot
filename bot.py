import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)
from filters import filters
from handlers import start, handle_callback
from fastapi import FastAPI, Request
import asyncio

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Змінні середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не встановлено в середовищі")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не встановлено в середовищі")

# Telegram bot
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Обробники
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_callback))

# FastAPI
app = FastAPI()

# Встановлення webhook під час запуску
@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logging.info("Webhook встановлено")

@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Bot is alive!"}

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=10000)
