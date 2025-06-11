import aiohttp
import asyncio
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from telegram import Update

EXCHANGES = ['Bybit', 'MEXC', 'KuCoin', 'BingX', 'Gate']

TRADING_FEES = {
    'KuCoin': 0.001,
    'MEXC': 0.001,
    'Bybit': 0.001,
    'BingX': 0.001,
    'Gate': 0.002
}

WITHDRAWAL_FEES = {
    'USDT': {
        'KuCoin': {'TRC20': 1, 'ERC20': 25},
        'MEXC': {'TRC20': 1},
        'Bybit': {'TRC20': 1},
        'BingX': {'TRC20': 1},
        'Gate': {'TRC20': 1}
    }
}

SYMBOL_ENDPOINTS = {
    'KuCoin': 'https://api.kucoin.com/api/v1/symbols',
    'MEXC': 'https://api.mexc.com/api/v3/exchangeInfo',
    'Bybit': 'https://api.bybit.com/v5/market/instruments?category=spot',
    'BingX': 'https://open-api.bingx.com/openApi/spot/v1/common/symbols',
    'Gate': 'https://api.gate.io/api/v4/spot/currency_pairs'
}

async def fetch_withdraw_status():
    result = {}
    async with aiohttp.ClientSession() as session:
        kucoin_resp = await session.get("https://api.kucoin.com/api/v1/currencies")
        kucoin_data = await kucoin_resp.json()
        result['KuCoin'] = {item['currency']: item['isWithdrawEnabled'] for item in kucoin_data['data']}

        bybit_resp = await session.get("https://api.bybit.com/v5/asset/coin/query-info")
        bybit_data = await bybit_resp.json()
        result['Bybit'] = {item['name']: any(chain['chainInfo']['chainType'] == 'TRC20' and chain['chainInfo']['canWithdraw'] for chain in item['chains']) for item in bybit_data['result']}

        gate_resp = await session.get("https://api.gate.io/api/v4/wallet/currency_chains")
        gate_data = await gate_resp.json()
        result['Gate'] = {}
        for item in gate_data:
            currency = item['currency']
            withdraw_disabled = item.get('withdraw_disabled', False)
            result['Gate'][currency.upper()] = not withdraw_disabled

        result['MEXC'] = {}
        result['BingX'] = {}

    return result

async def fetch_prices_from_exchanges():
    prices = {ex: {} for ex in EXCHANGES}
    async with aiohttp.ClientSession() as session:
        kucoin_resp = await session.get("https://api.kucoin.com/api/v1/market/allTickers")
        kucoin_data = await kucoin_resp.json()
        for item in kucoin_data['data']['ticker']:
            if item['symbol'].endswith("USDT"):
                prices['KuCoin'][item['symbol']] = float(item['last'])

        mexc_resp = await session.get("https://api.mexc.com/api/v3/ticker/price")
        mexc_data = await mexc_resp.json()
        for item in mexc_data:
            if item['symbol'].endswith("USDT"):
                prices['MEXC'][item['symbol']] = float(item['price'])

        bybit_resp = await session.get("https://api.bybit.com/v5/market/tickers?category=spot")
        bybit_data = await bybit_resp.json()
        for item in bybit_data['result']['list']:
            if item['symbol'].endswith("USDT"):
                prices['Bybit'][item['symbol']] = float(item['lastPrice'])

        bingx_resp = await session.get("https://open-api.bingx.com/openApi/spot/v1/ticker/price")
        bingx_data = await bingx_resp.json()
        for item in bingx_data['data']:
            if item['symbol'].endswith("USDT"):
                prices['BingX'][item['symbol']] = float(item['price'])

        gate_resp = await session.get("https://api.gate.io/api/v4/spot/tickers")
        gate_data = await gate_resp.json()
        for item in gate_data:
            if item['currency_pair'].endswith("_USDT"):
                symbol = item['currency_pair'].replace('_', '')
                prices['Gate'][symbol] = float(item['last'])

    return prices

def find_arbitrage_opportunities(prices, filters):
    signals = []
    symbols = set()
    now = time.time()

    for exchange_prices in prices.values():
        symbols.update(exchange_prices.keys())

    for symbol in symbols:
        if not filters.get('is_futures', False) and any(x in symbol for x in ['PERP', '-USD', '-USDT', 'USD_']):
            continue

        coin = symbol.replace("USDT", "")
        best_buy = None
        best_sell = None

        for ex in EXCHANGES:
            price = prices.get(ex, {}).get(symbol)
            if price:
                if filters['exchanges_buy'].get(ex, False):
                    if not best_buy or price < best_buy[1]:
                        best_buy = (ex, price)
                if filters['exchanges_sell'].get(ex, False):
                    if not best_sell or price > best_sell[1]:
                        best_sell = (ex, price)

        if best_buy and best_sell and best_buy[0] != best_sell[0]:
            buy_ex, buy_price = best_buy
            sell_ex, sell_price = best_sell
            fee_buy = buy_price * TRADING_FEES[buy_ex]
            fee_sell = sell_price * TRADING_FEES[sell_ex]
            spread = (sell_price - buy_price - fee_buy - fee_sell) / buy_price * 100
            volume = filters['budget']

            withdraw_network = 'TRC20'
            withdraw_fee = WITHDRAWAL_FEES.get('USDT', {}).get(buy_ex, {}).get(withdraw_network, 0)
            spread_after_withdraw = (sell_price - buy_price - fee_buy - fee_sell - withdraw_fee) / buy_price * 100

            signal_age = 0

            if spread_after_withdraw >= filters['min_profit'] and volume >= filters['min_volume'] and signal_age <= filters['max_lifetime']:
                signals.append({
                    'coin': coin,
                    'buy_exchange': buy_ex,
                    'sell_exchange': sell_ex,
                    'spread': round(spread_after_withdraw, 2),
                    'volume': volume,
                    'buy_price': buy_price,
                    'sell_price': sell_price,
                    'withdraw_fee': withdraw_fee,
                    'network': withdraw_network,
                    'timestamp': now
                })
    return signals

def build_filters_menu(filters):
    keyboard = [
        [
            InlineKeyboardButton(f"Мін. профіт: {filters['min_profit']}%", callback_data='set_min_profit'),
            InlineKeyboardButton(f"Обсяг: {filters['min_volume']}$", callback_data='set_min_volume')
        ],
        [
            InlineKeyboardButton("Бюджет: ${}".format(filters.get('budget', 100)), callback_data='set_budget')
        ],
        [
            InlineKeyboardButton("Биржі покупки", callback_data='toggle_buy_exchanges'),
            InlineKeyboardButton("Биржі продажу", callback_data='toggle_sell_exchanges')
        ],
        [
            InlineKeyboardButton(f"Ф’ючерси: {'✅' if filters.get('is_futures', False) else '❌'}", callback_data='toggle_futures')
        ],
        [
            InlineKeyboardButton(f"⏱ Життя: {filters.get('max_lifetime', 30)}с", callback_data='set_max_lifetime')
        ],
        [
            InlineKeyboardButton("🔄 Оновити", callback_data='refresh_signals')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def handle_filter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    filters = context.user_data.get('filters', {
        'min_profit': 0.8,
        'min_volume': 10,
        'budget': 100,
        'is_futures': False,
        'exchanges_buy': {ex: True for ex in EXCHANGES},
        'exchanges_sell': {ex: True for ex in EXCHANGES},
        'max_lifetime': 30
    })

    if query.data == 'set_min_profit':
        filters['min_profit'] += 0.2
        if filters['min_profit'] > 5:
            filters['min_profit'] = 0.8

    elif query.data == 'set_min_volume':
        filters['min_volume'] += 10
        if filters['min_volume'] > 100:
            filters['min_volume'] = 10

    elif query.data == 'set_budget':
        filters['budget'] *= 2
        if filters['budget'] > 1000:
            filters['budget'] = 50

    elif query.data == 'toggle_buy_exchanges':
        for ex in filters['exchanges_buy']:
            filters['exchanges_buy'][ex] = not filters['exchanges_buy'][ex]

    elif query.data == 'toggle_sell_exchanges':
        for ex in filters['exchanges_sell']:
            filters['exchanges_sell'][ex] = not filters['exchanges_sell'][ex]

    elif query.data == 'toggle_futures':
        filters['is_futures'] = not filters.get('is_futures', False)

    elif query.data == 'set_max_lifetime':
        filters['max_lifetime'] += 10
        if filters['max_lifetime'] > 300:
            filters['max_lifetime'] = 30

    context.user_data['filters'] = filters
    await query.edit_message_reply_markup(reply_markup=build_filters_menu(filters))
