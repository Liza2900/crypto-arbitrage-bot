import logging
import os
import asyncio
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

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Додаємо URL
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не встановлено в середовищі")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не встановлено в середовищі")

# Telegram app
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_callback))

# FastAPI app
app = FastAPI()

@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Bot is alive!"}

# Set webhook
async def set_webhook():
    await application.bot.set_webhook(url=WEBHOOK_URL)
    print("✅ Webhook встановлено:", WEBHOOK_URL)

import asyncio

@app.on_event("startup")
async def on_startup():
    await set_webhook()


# Run Uvicorn server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=10000)


