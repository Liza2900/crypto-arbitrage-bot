import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from filters import (
    fetch_prices_from_exchanges,
    find_arbitrage_opportunities,
    build_filters_menu,
    handle_filter_callback,
    EXCHANGES
)
from fastapi import FastAPI, Request
import asyncio

# Логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Змінні середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не встановлено")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не встановлено")

# Telegram Application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Стандартні фільтри
def default_filters():
    return {
        'min_profit': 0.8,
        'min_volume': 10,
        'budget': 100,
        'is_futures': False,
        'exchanges_buy': {ex: True for ex in EXCHANGES},
        'exchanges_sell': {ex: True for ex in EXCHANGES},
        'max_lifetime': 30
    }

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['filters'] = default_filters()
    await update.message.reply_text("🔍 Виберіть фільтри для пошуку арбітражу:",
                                    reply_markup=build_filters_menu(context.user_data['filters']))

# /search
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = context.user_data.get('filters', default_filters())
    await update.message.reply_text("⏳ Пошук можливостей арбітражу...")

    prices = await fetch_prices_from_exchanges()
    signals = find_arbitrage_opportunities(prices, filters)

    if not signals:
        await update.message.reply_text("❌ Немає можливостей арбітражу за поточними фільтрами.")
    else:
        for sig in signals:
            net_profit = (sig['spread'] / 100) * filters['budget'] - sig['withdraw_fee']
            msg = (
                f"💰 <b>{sig['coin']} Арбітраж</b>\n"
                f"📉 Купити на: <b>{sig['buy_exchange']}</b> — <code>${sig['buy_price']:.4f}</code>\n"
                f"📈 Продати на: <b>{sig['sell_exchange']}</b> — <code>${sig['sell_price']:.4f}</code>\n"
                f"📦 Обсяг: <code>${sig['volume']}</code>\n"
                f"🔁 Мережа: <b>{sig['network']}</b>\n"
                f"💸 Комісія виводу: <code>${sig['withdraw_fee']}</code>\n"
                f"📊 Спред після комісії: <code>{net_profit:.2f}$ ({sig['spread']}%)</code>\n"
                f"✅ Вивід доступний: <b>{'✅' if sig.get('is_withdrawable', True) else '❌'}</b>\n"
                f"⏱ Час переказу: <code>{sig.get('transfer_time', 'N/A')}</code>\n"
            )
            await update.message.reply_text(msg, parse_mode='HTML')

# Додаємо обробники
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("search", search))
application.add_handler(CallbackQueryHandler(handle_filter_callback))

# FastAPI app
app = FastAPI()

@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logging.info("Webhook встановлено")

@app.post("/")
async def webhook_handler(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

@app.get("/")
def home():
    return {"message": "Arbitrage Bot is running"}

