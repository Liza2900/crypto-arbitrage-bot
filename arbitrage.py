import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from filters import build_filters_menu, handle_filter_callback, fetch_prices_from_exchanges, find_arbitrage_opportunities


logging.basicConfig(level=logging.INFO)

user_filters = {
    'min_profit': 0.8,
    'min_volume': 10,
    'budget': 100,
    'is_futures': False,
    'exchanges_buy': {
        'KuCoin': True, 'MEXC': True, 'Bybit': True, 'BingX': True, 'Gate': True
    },
    'exchanges_sell': {
        'KuCoin': True, 'MEXC': True, 'Bybit': True, 'BingX': True, 'Gate': True
    },
    'max_lifetime': 30
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['filters'] = user_filters.copy()
    await update.message.reply_text("\u2705 Фільтри для арбітражу:", reply_markup=build_filters_menu(context.user_data['filters']))


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = context.user_data.get('filters', user_filters)
    await update.message.reply_text("\u231B Збираю дані з бірж...")
    prices = await fetch_prices_from_exchanges()
    signals = find_arbitrage_opportunities(prices, filters)

    if not signals:
        await update.message.reply_text("\u274C Немає відповідних арбітражних можливостей.")
    else:
        for sig in signals[:10]:
            msg = (
                f"\u2728 <b>{sig['coin']}</b> | {sig['spread']}% прибуток\n"
                f"Купити на: {sig['buy_exchange']} @ {sig['buy_price']}$\n"
                f"Продати на: {sig['sell_exchange']} @ {sig['sell_price']}$\n"
                f"\u2197 Обсяг: {sig['volume']}$ | Комісія виводу: {sig['withdraw_fee']}$ ({sig['network']})"
            )
            await update.message.reply_text(msg, parse_mode='HTML')


if __name__ == '__main__':
    app = ApplicationBuilder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CallbackQueryHandler(handle_filter_callback))

    app.run_polling()



