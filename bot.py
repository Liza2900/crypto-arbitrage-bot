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

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен з environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не встановлено в середовищі")

# Telegram bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Обробники
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_callback))

# FastAPI
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

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=10000)

