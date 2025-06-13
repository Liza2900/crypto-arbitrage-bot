import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from filters import (
    build_filters_menu,
    handle_filter_callback,
    EXCHANGES
)
from arbitrage import fetch_prices_from_exchanges, find_arbitrage_opportunities

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Змінні середовища
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

if not TOKEN:
    raise ValueError("BOT_TOKEN не встановлено в середовищі")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не встановлено в середовищі")

# Початкові фільтри за замовчуванням
def default_filters():
    return {
        'min_profit': 0.8,
        'min_volume': 10,
        'budget': 100,
        'is_futures': False,
        'exchanges_buy': {ex: True for ex in EXCHANGES},
        'exchanges_sell': {ex: True for ex in EXCHANGES},
        'max_lifetime': 30,
        'last_search_id': None  # додано для захисту від повторної обробки
    }

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['filters'] = default_filters()
    await update.message.reply_text("🔍 Виберіть фільтри для пошуку арбітражу:",
                                    reply_markup=build_filters_menu(context.user_data['filters']))

# Команда /filters
async def filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = context.user_data.get('filters', default_filters())
    await update.message.reply_text("🔧 Змініть фільтри для пошуку арбітражу:",
                                    reply_markup=build_filters_menu(filters))

# Команда /search
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = context.user_data.get('filters', default_filters())

    # Унікальний ID для кожного запиту
    search_id = update.update_id
    if filters.get("last_search_id") == search_id:
        logger.info("🔁 Повторний запит /search — ігноруємо")
        return
    filters["last_search_id"] = search_id

    await update.message.reply_text("⏳ Пошук можливостей арбітражу...")

    logger.info("🔎 Починаємо завантаження цін з бірж...")
    prices = await fetch_prices_from_exchanges()
    total_pairs = sum(len(p) for p in prices.values())
    logger.info(f"✅ Отримано ціни: {total_pairs} валютних пар")

    if not prices:
        await update.message.reply_text("⚠️ Не вдалося отримати ціни з бірж.")
        return

    logger.info("📊 Шукаємо можливості арбітражу...")
    signals = find_arbitrage_opportunities(prices, filters)
    logger.info(f"✅ Знайдено {len(signals)} можливих сигналів")

    if not signals:
        await update.message.reply_text("❌ Немає можливостей арбітражу за поточними фільтрами.")
    else:
        sig = signals[0]  # Надсилаємо тільки перший спред
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
        logger.info(f"📤 Надсилаємо арбітраж для {sig['coin']}")
        await update.message.reply_text(msg, parse_mode='HTML')

# FastAPI app
app = FastAPI()
application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("search", search))
application.add_handler(CommandHandler("filters", filters_command))
application.add_handler(CallbackQueryHandler(handle_filter_callback))

@app.on_event("startup")
async def startup():
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=PORT, reload=False)
