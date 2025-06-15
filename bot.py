import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, ContextTypes, CommandHandler,
                          MessageHandler, CallbackQueryHandler, filters)
from arbitrage import fetch_prices_from_exchanges, find_arbitrage_opportunities, EXCHANGES

from dotenv import load_dotenv
load_dotenv()

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

def get_user_filters(context):
    if "filters" not in context.user_data:
        context.user_data["filters"] = DEFAULT_FILTERS.copy()
    return context.user_data["filters"]

def build_filters_menu(filters):
    keyboard = [
        [InlineKeyboardButton(f"📦 Мін. обсяг: {filters['min_volume']}$", callback_data="set_min_volume")],
        [InlineKeyboardButton(f"💰 Мін. прибуток: {filters['min_profit']}%", callback_data="set_min_profit")],
        [InlineKeyboardButton(f"🧾 Бюджет: {filters['budget']}$", callback_data="set_budget")],
        [InlineKeyboardButton("🔁 Оновити", callback_data="refresh")]
    ]

    keyboard.append([InlineKeyboardButton("Біржі купівлі", callback_data="toggle_buy_exchanges")])
    keyboard.append([InlineKeyboardButton("Біржі продажу", callback_data="toggle_sell_exchanges")])

    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_filters")])

    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Натисни /search, щоб знайти арбітражні можливості.")

async def filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = get_user_filters(context)
    await update.message.reply_text("🔧 Поточні фільтри:", reply_markup=build_filters_menu(filters))

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = get_user_filters(context)

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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    filters = get_user_filters(context)

    if query.data == "set_min_profit":
        context.user_data["awaiting"] = "min_profit"
        await query.edit_message_text("Введи новий мінімальний прибуток у %:")
    elif query.data == "set_min_volume":
        context.user_data["awaiting"] = "min_volume"
        await query.edit_message_text("Введи новий мінімальний обсяг у $:\n\nℹ️ Рекомендуємо 10–30$ для бюджету до 100$")
    elif query.data == "set_budget":
        context.user_data["awaiting"] = "budget"
        await query.edit_message_text("Введи новий бюджет у $:")
    elif query.data == "refresh":
        await query.edit_message_text("🔁 Оновлюємо дані...")
        await search(update, context)
    elif query.data == "toggle_buy_exchanges":
        buttons = [
            [InlineKeyboardButton(f"{'✅' if filters['exchanges_buy'][ex] else '❌'} {ex}", callback_data=f"toggle_buy_{ex}")]
            for ex in EXCHANGES.keys()
        ]
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_filters")])
        await query.edit_message_text("🔘 Виберіть біржі для КУПІВЛІ:", reply_markup=InlineKeyboardMarkup(buttons))
    elif query.data == "toggle_sell_exchanges":
        buttons = [
            [InlineKeyboardButton(f"{'✅' if filters['exchanges_sell'][ex] else '❌'} {ex}", callback_data=f"toggle_sell_{ex}")]
            for ex in EXCHANGES.keys()
        ]
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_filters")])
        await query.edit_message_text("🔘 Виберіть біржі для ПРОДАЖУ:", reply_markup=InlineKeyboardMarkup(buttons))
    elif query.data.startswith("toggle_buy_"):
        ex = query.data.split("toggle_buy_")[1]
        filters['exchanges_buy'][ex] = not filters['exchanges_buy'][ex]
        buttons = [
            [InlineKeyboardButton(f"{'✅' if filters['exchanges_buy'][ex2] else '❌'} {ex2}", callback_data=f"toggle_buy_{ex2}")]
            for ex2 in EXCHANGES.keys()
        ]
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_filters")])
        await query.edit_message_text("🔘 Виберіть біржі для КУПІВЛІ:", reply_markup=InlineKeyboardMarkup(buttons))
    elif query.data.startswith("toggle_sell_"):
        ex = query.data.split("toggle_sell_")[1]
        filters['exchanges_sell'][ex] = not filters['exchanges_sell'][ex]
        buttons = [
            [InlineKeyboardButton(f"{'✅' if filters['exchanges_sell'][ex2] else '❌'} {ex2}", callback_data=f"toggle_sell_{ex2}")]
            for ex2 in EXCHANGES.keys()
        ]
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_filters")])
        await query.edit_message_text("🔘 Виберіть біржі для ПРОДАЖУ:", reply_markup=InlineKeyboardMarkup(buttons))
    elif query.data == "back_to_filters":
        await filters_command(update, context)

async def text_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    awaiting = context.user_data.get("awaiting")
    if not awaiting:
        return

    try:
        value = float(update.message.text)
        filters = get_user_filters(context)
        filters[awaiting] = value
        context.user_data["awaiting"] = None
        await update.message.reply_text(f"✅ Фільтр '{awaiting}' оновлено до {value}.", reply_markup=build_filters_menu(filters))
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
