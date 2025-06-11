from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from arbitrage import generate_arbitrage_signals


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔍 Знайти арбітраж", callback_data="find")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привіт! Натисни кнопку нижче, щоб знайти арбітражні можливості:",
        reply_markup=reply_markup
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    filters = {
        "min_profit": 0.8,
        "min_volume": 10,
        "exchanges_buy": {
            "Bybit": True,
            "MEXC": True,
            "KuCoin": True,
            "BingX": True,
            "Gate": True,
        },
        "exchanges_sell": {
            "Bybit": True,
            "MEXC": True,
            "KuCoin": True,
            "BingX": True,
            "Gate": True,
        },
    }

    await query.edit_message_text("⏳ Збираю дані з бірж...")

    signals = await generate_arbitrage_signals(filters)

    if not signals:
        await query.message.reply_text("❌ Не знайдено арбітражних можливостей.")
        return

    for signal in signals[:10]:  # максимум 10 сигналів
        msg = (
            f"📈 <b>{signal['coin']}</b>\n"
            f"🔽 Купити на: <b>{signal['buy_exchange']}</b> — {signal['buy_price']} USDT\n"
            f"🔼 Продати на: <b>{signal['sell_exchange']}</b> — {signal['sell_price']} USDT\n"
            f"📊 Профіт: <b>{signal['spread']}%</b>\n"
            f"📦 Обсяг: {signal['volume']} USDT\n"
            f"🔗 Мережа: {signal['network']}\n"
            f"⏱ Трансфер: {signal['transfer_time']}\n"
        )
        await query.message.reply_text(msg, parse_mode="HTML")
