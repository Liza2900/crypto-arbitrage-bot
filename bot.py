import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, ContextTypes, CommandHandler,
                          MessageHandler, CallbackQueryHandler, filters)
from arbitrage import fetch_prices_from_exchanges, find_arbitrage_opportunities, EXCHANGES

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_FILTERS = {
    'min_volume': 10,
    'min_profit': 0.8,
    'budget': 100,
    'exchanges_buy': {ex: True for ex in EXCHANGES.keys()},
    'exchanges_sell': {ex: True for ex in EXCHANGES.keys()}
}

def build_filters_menu(filters):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📦 Мін. обсяг: {filters['min_volume']}$", callback_data="set_min_volume")],
        [InlineKeyboardButton(f"💰 Мін. прибуток: {filters['min_profit']}%", callback_data="set_min_profit")],
        [InlineKeyboardButton(f"🧾 Бюджет: {filters['budget']}$", callback_data="set_budget")],
        [InlineKeyboardButton("🔁 Оновити", callback_data="refresh")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Натисни /search, щоб знайти арбітражні можливості.")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = context.user_data.get("filters", DEFAULT_FILTERS.copy())
    for key, value in DEFAULT_FILTERS.items():
        if key not in filters:
            filters[key] = value

    await update.message.reply_text("🔎 Починаємо завантаження цін з бірж...")
    prices = await fetch_prices_from_exchanges()
    await update.message.reply_text(f"✅ Отримано ціни: {sum(len(p) for p in prices.values())} валютних пар")

    await update.message.reply_text("📊 Шукаємо можливості арбітражу...")
    signals = find_arbitrage_opportunities(prices, filters)

    if not signals:
        await update.message.reply_text("❌ Можливостей не знайдено. Спробуйте з іншими фільтрами.")
        return

    for sig in signals:
        msg = (
            f"💸 {sig['coin']}: {sig['buy_exchange']} → {sig['sell_exchange']}\n"
            f"• Купівля: {sig['buy_price']}$\n"
            f"• Продаж: {sig['sell_price']}$\n"
            f"• Профіт: {sig['spread']}%\n"
            f"• Обсяг: {sig['volume']}$\n"
            f"• Комісія виводу: {sig['withdraw_fee']}\n"
            f"• Мережа: {sig['network']}\n"
            f"• Час переказу: {sig['transfer_time']}"
        )
        await update.message.reply_text(msg)

async def filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = context.user_data.get("filters", DEFAULT_FILTERS.copy())
    await update.message.reply_text("⚙️ Налаштування фільтрів:", reply_markup=build_filters_menu(filters))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    filters = context.user_data.get("filters", DEFAULT_FILTERS.copy())

    if query.data == "set_min_profit":
        context.user_data["awaiting"] = "min_profit"
        await query.edit_message_text("Введи новий мінімальний прибуток у %:")
    elif query.data == "set_min_volume":
        context.user_data["awaiting"] = "min_volume"
        await query.edit_message_text("Введи новий мінімальний обсяг у $:")
    elif query.data == "set_budget":
        context.user_data["awaiting"] = "budget"
        await query.edit_message_text("Введи новий бюджет у $:")
    elif query.data == "refresh":
        await search(update, context)
    elif query.data == "show_filters":
        await query.edit_message_text("⚙️ Налаштування фільтрів:", reply_markup=build_filters_menu(filters))
    else:
        await query.edit_message_text("⚙️ Фільтри поки що не змінюються. У розробці.")

async def text_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    awaiting = context.user_data.get("awaiting")
    if not awaiting:
        return

    try:
        value = float(update.message.text)
        context.user_data.setdefault("filters", DEFAULT_FILTERS.copy())[awaiting] = value
        context.user_data["awaiting"] = None
        await update.message.reply_text(f"✅ Фільтр '{awaiting}' оновлено до {value}.", reply_markup=build_filters_menu(context.user_data["filters"]))
    except ValueError:
        await update.message.reply_text("❌ Введено не число. Спробуй ще раз.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("filters", filters_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_input_handler))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/"
    )

