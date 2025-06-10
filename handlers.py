from telegram import Update
from telegram.ext import ContextTypes
from filters_config import user_filters
from keyboards import main_menu_keyboard, filter_keyboard
from arbitrage import generate_arbitrage_signals

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in user_filters:
        # Ініціалізуємо фільтри за замовчуванням
        user_filters[chat_id] = {
            "min_profit": 0.8,
            "min_volume": 10,
            "exchanges_buy": {
                "KuCoin": True,
                "MEXC": True,
                "OKX": True,
                "Bitget": True,
                "BingX": True,
                "Gate.io": True,
                "Bybit": True
            },
            "exchanges_sell": {
                "KuCoin": True,
                "MEXC": True,
                "OKX": True,
                "Bitget": True,
                "BingX": True,
                "Gate.io": True,
                "Bybit": True
            }
        }

    await update.message.reply_text(
        "👋 Привіт! Обери дію:",
        reply_markup=main_menu_keyboard(user_filters[chat_id])
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    filters = user_filters[chat_id]

    if query.data == "start_search":
        signals = generate_arbitrage_signals(filters)
        if not signals:
            await query.edit_message_text("Немає підходящих арбітражних можливостей за заданими фільтрами.")
        else:
            for signal in signals:
                text = (
                    f"📊 Арбітраж: {signal['coin']}/USDT\n"
                    f"🔄 Купити на {signal['buy_exchange']} → Продати на {signal['sell_exchange']}\n"
                    f"💰 Профіт: {signal['spread']}%\n"
                    f"📦 Обсяг: ~{signal['volume']} USDT\n"
                    f"💸 Купівля: {signal['buy_exchange']} – {signal['buy_price']}\n"
                    f"💰 Продаж: {signal['sell_exchange']} – {signal['sell_price']}\n"
                    f"🌐 Мережа: {signal['network']}\n"
                    f"⏱️ Живе вже: {signal['age']}, Переклад: {signal['transfer_time']}\n"
                    f"📉 Ф'ючерси: {', '.join(signal['futures_exchanges'])}"
                )
                await context.bot.send_message(chat_id=chat_id, text=text)

    elif query.data == "filters":
        await query.edit_message_text(
            "🔧 Налаштування фільтрів:",
            reply_markup=filter_keyboard(filters)
        )

    elif query.data.startswith("filter_profit"):
        filters["min_profit"] += 0.2
        if filters["min_profit"] > 5:
            filters["min_profit"] = 0.8
        await query.edit_message_reply_markup(reply_markup=filter_keyboard(filters))

    elif query.data.startswith("filter_volume"):
        filters["min_volume"] += 10
        if filters["min_volume"] > 100:
            filters["min_volume"] = 10
        await query.edit_message_reply_markup(reply_markup=filter_keyboard(filters))

    elif query.data.startswith("exchange_buy_"):
        ex = query.data.split("exchange_buy_")[1]
        filters["exchanges_buy"][ex] = not filters["exchanges_buy"][ex]
        await query.edit_message_reply_markup(reply_markup=filter_keyboard(filters))

    elif query.data.startswith("exchange_sell_"):
        ex = query.data.split("exchange_sell_")[1]
        filters["exchanges_sell"][ex] = not filters["exchanges_sell"][ex]
        await query.edit_message_reply_markup(reply_markup=filter_keyboard(filters))

