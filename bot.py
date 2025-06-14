import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters as tg_filters, ContextTypes
from filters import (
    build_filters_menu,
    handle_filter_callback,
    EXCHANGES
)
from arbitrage import fetch_prices_from_exchanges, find_arbitrage_opportunities
import random

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
        'budget': 100,
        'is_futures': False,
        'exchanges_buy': {ex: True for ex in EXCHANGES},
        'exchanges_sell': {ex: True for ex in EXCHANGES},
        'max_lifetime': 30,
        'last_search_id': None,
        'sort_random': True
    }

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['filters'] = default_filters()
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("🔧 Фільтри"), KeyboardButton("🔍 Пошук")]],
        resize_keyboard=True
    )
    await update.message.reply_text("🔍 Виберіть фільтри для пошуку арбітражу:",
                                    reply_markup=keyboard)
    await update.message.reply_text("⬇️ Меню фільтрів:",
                                    reply_markup=build_filters_menu(context.user_data['filters']))

# Обробка текстових кнопок
async def handle_text_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔧 Фільтри":
        filters = context.user_data.get('filters', default_filters())
        await update.message.reply_text("🔧 Змініть фільтри для пошуку арбітражу:",
                                        reply_markup=build_filters_menu(filters))
    elif update.message.text == "🔍 Пошук":
        await search(update, context)

# Обробка введення вручну
async def handle_manual_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'awaiting_input' not in context.user_data:
        return

    field = context.user_data.pop('awaiting_input')
    text = update.message.text

    try:
        value = float(text)
    except ValueError:
        await update.message.reply_text("❌ Введіть число.")
        return

    filters = context.user_data.get('filters', default_filters())
    filters[field] = value
    context.user_data['filters'] = filters
    await update.message.reply_text("✅ Змінено фільтр.", reply_markup=build_filters_menu(filters))

# Команда /search
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = context.user_data.get('filters', default_filters())

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

    signals = [s for s in signals if s['coin'] not in ('BTC', 'ETH')]

    if not signals:
        await update.message.reply_text("❌ Немає можливостей арбітражу за поточними фільтрами.")
        return

    if filters.get('sort_random', True):
        random.shuffle(signals)
    else:
        signals.sort(key=lambda s: s['spread'], reverse=True)

    context.user_data['signals'] = signals
    context.user_data['signal_index'] = 0

    await send_signal(update.message.reply_text, signals[0], filters)

async def send_signal(send_func, signal, filters):
    net_profit = (signal['spread'] / 100) * filters['budget'] - signal['withdraw_fee']
    msg = (
        f"💰 <b>{signal['coin']} Арбітраж</b>\n"
        f"📉 Купити на: <b>{signal['buy_exchange']}</b> — <code>${int(signal['buy_price'])}</code>\n"
        f"📈 Продати на: <b>{signal['sell_exchange']}</b> — <code>${int(signal['sell_price'])}</code>\n"
        f"📦 Обсяг: <code>${int(signal['volume'])}</code>\n"
        f"📊 Ціна за 1 монету: Купівля — <code>${signal['buy_price']:.4f}</code>, Продаж — <code>${signal['sell_price']:.4f}</code>\n"
        f"🔁 Мережа: <b>{signal['network']}</b>\n"
        f"💸 Комісія виводу: <code>${signal['withdraw_fee']}</code>\n"
        f"📊 Спред після комісії: <code>{net_profit:.2f}$ ({signal['spread']}%)</code>\n"
        f"✅ Вивід доступний: <b>{'✅' if signal.get('is_withdrawable', True) else '❌'}</b>\n"
        f"⏱ Час переказу: <code>{signal.get('transfer_time', 'N/A')}</code>\n"
    )
    keyboard = [
        [InlineKeyboardButton("➡️ Наступний", callback_data="next_signal")],
        [InlineKeyboardButton("🔁 Оновити", callback_data="refresh_signals")]
    ]
    await send_func(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_next_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    index = context.user_data.get('signal_index', 0) + 1
    signals = context.user_data.get('signals', [])

    if index >= len(signals):
        await query.edit_message_text("✅ Це був останній сигнал.")
        return

    context.user_data['signal_index'] = index
    await send_signal(query.edit_message_text, signals[index], context.user_data.get('filters', default_filters()))

async def handle_refresh_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await search(query, context)

# FastAPI app
app = FastAPI()
application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("search", search))
application.add_handler(CommandHandler("filters", handle_text_commands))
application.add_handler(CallbackQueryHandler(handle_filter_callback))
application.add_handler(CallbackQueryHandler(handle_next_signal, pattern="^next_signal$"))
application.add_handler(CallbackQueryHandler(handle_refresh_signal, pattern="^refresh_signals$"))
application.add_handler(MessageHandler(tg_filters.TEXT & (~tg_filters.COMMAND), handle_manual_input))
application.add_handler(MessageHandler(tg_filters.TEXT & (~tg_filters.COMMAND), handle_text_commands))

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
