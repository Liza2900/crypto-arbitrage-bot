import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from filters import (
    fetch_prices_from_exchanges,
    find_arbitrage_opportunities,
    build_filters_menu,
    handle_filter_callback,
    EXCHANGES
)

TOKEN = "YOUR_BOT_TOKEN"

# Початкові фільтри за замовчуванням
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

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['filters'] = default_filters()
    await update.message.reply_text("🔍 Виберіть фільтри для пошуку арбітражу:",
                                    reply_markup=build_filters_menu(context.user_data['filters']))

# Обробка /search — знаходить сигнали і надсилає
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = context.user_data.get('filters', default_filters())
    await update.message.reply_text("⏳ Пошук можливостей арбітражу...")
    
    prices = await fetch_prices_from_exchanges()
    signals = find_arbitrage_opportunities(prices, filters)

    if not signals:
        await update.message.reply_text("❌ Немає можливостей арбітражу за поточними фільтрами.")
    else:
        for sig in signals:
            msg = (
                f"💰 {sig['coin']} Арбітраж
"
                f"Купити на: {sig['buy_exchange']} — ${sig['buy_price']:.4f}
"
                f"Продати на: {sig['sell_exchange']} — ${sig['sell_price']:.4f}
"
                f"🔁 Мережа: {sig['network']}, Комісія: ${sig['withdraw_fee']}
"
                f"📊 Спред: {sig['spread']}%
"
                f"📦 Обсяг: ${sig['volume']}")
            await update.message.reply_text(msg)

# Головна функція запуску
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CallbackQueryHandler(handle_filter_callback))

    print("🚀 Бот запущено")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())




