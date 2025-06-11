import aiohttp
import asyncio

EXCHANGES = ['Bybit', 'MEXC', 'KuCoin', 'BingX', 'Gate']

SYMBOL_ENDPOINTS = {
    'KuCoin': 'https://api.kucoin.com/api/v1/symbols',
    'MEXC': 'https://api.mexc.com/api/v3/exchangeInfo',
    'Bybit': 'https://api.bybit.com/v5/market/instruments?category=spot',
    'BingX': 'https://open-api.bingx.com/openApi/spot/v1/common/symbols',
    'Gate': 'https://api.gate.io/api/v4/spot/currency_pairs'
}

async def fetch_price_kucoin(session, symbol):
    url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}"
    async with session.get(url) as resp:
        data = await resp.json()
        return 'KuCoin', float(data['data']['bestBid']), float(data['data']['bestAsk'])

async def fetch_price_mexc(session, symbol):
    url = f"https://api.mexc.com/api/v3/ticker/bookTicker?symbol={symbol}"
    async with session.get(url) as resp:
        data = await resp.json()
        return 'MEXC', float(data['bidPrice']), float(data['askPrice'])

async def fetch_price_bybit(session, symbol):
    url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
    async with session.get(url) as resp:
        data = await resp.json()
        ticker = data['result']['list'][0]
        return 'Bybit', float(ticker['bid1Price']), float(ticker['ask1Price'])

async def fetch_price_bingx(session, symbol):
    url = f"https://open-api.bingx.com/openApi/spot/v1/ticker/24hr?symbol={symbol}"
    async with session.get(url) as resp:
        data = await resp.json()
        return 'BingX', float(data['data']['bidPrice']), float(data['data']['askPrice'])

async def fetch_price_gate(session, symbol):
    url = f"https://api.gate.io/api/v4/spot/order_book?currency_pair={symbol}&limit=1"
    async with session.get(url) as resp:
        data = await resp.json()
        return 'Gate', float(data['bids'][0][0]), float(data['asks'][0][0])

async def fetch_all_symbols():
    symbol_map = {}
    async with aiohttp.ClientSession() as session:
        kucoin_resp = await session.get(SYMBOL_ENDPOINTS['KuCoin'])
        kucoin_data = await kucoin_resp.json()
        for item in kucoin_data['data']:
            if item['quoteCurrency'] == 'USDT':
                base = item['baseCurrency']
                symbol_map.setdefault(base, {})['KuCoin'] = item['symbol']

        mexc_resp = await session.get(SYMBOL_ENDPOINTS['MEXC'])
        mexc_data = await mexc_resp.json()
        for item in mexc_data['symbols']:
            if item['quoteAsset'] == 'USDT':
                base = item['baseAsset']
                symbol_map.setdefault(base, {})['MEXC'] = item['symbol']

        bybit_resp = await session.get(SYMBOL_ENDPOINTS['Bybit'])
        bybit_data = await bybit_resp.json()
        for item in bybit_data['result']['list']:
            if item['quoteCoin'] == 'USDT':
                base = item['baseCoin']
                symbol_map.setdefault(base, {})['Bybit'] = item['symbol']

        bingx_resp = await session.get(SYMBOL_ENDPOINTS['BingX'])
        bingx_data = await bingx_resp.json()
        for item in bingx_data['data']:
            if item['quoteAsset'] == 'USDT':
                base = item['baseAsset']
                symbol_map.setdefault(base, {})['BingX'] = item['symbol']

        gate_resp = await session.get(SYMBOL_ENDPOINTS['Gate'])
        gate_data = await gate_resp.json()
        for item in gate_data:
            if item['quote'] == 'USDT':
                base = item['base']
                symbol_map.setdefault(base, {})['Gate'] = item['id']

    return symbol_map

async def generate_arbitrage_signals(filters):
    signals = []
    symbol_map = await fetch_all_symbols()
    coins = [coin for coin, exchanges in symbol_map.items() if len(exchanges) >= 2]

    async with aiohttp.ClientSession() as session:
        for coin in coins:
            subtasks = []
            for ex in EXCHANGES:
                if filters['exchanges_buy'].get(ex, False) or filters['exchanges_sell'].get(ex, False):
                    if ex not in symbol_map[coin]:
                        continue
                    symbol = symbol_map[coin][ex]
                    if ex == 'KuCoin':
                        subtasks.append(fetch_price_kucoin(session, symbol))
                    elif ex == 'MEXC':
                        subtasks.append(fetch_price_mexc(session, symbol))
                    elif ex == 'Bybit':
                        subtasks.append(fetch_price_bybit(session, symbol))
                    elif ex == 'BingX':
                        subtasks.append(fetch_price_bingx(session, symbol))
                    elif ex == 'Gate':
                        subtasks.append(fetch_price_gate(session, symbol))

            prices = await asyncio.gather(*subtasks, return_exceptions=True)
            valid_prices = [p for p in prices if not isinstance(p, Exception)]

            for buy in valid_prices:
                for sell in valid_prices:
                    if buy[0] == sell[0]:
                        continue
                    spread = (sell[1] - buy[2]) / buy[2] * 100
                    if spread >= filters['min_profit']:
                        signal = {
                            'coin': coin,
                            'buy_exchange': buy[0],
                            'sell_exchange': sell[0],
                            'spread': round(spread, 2),
                            'volume': 100,
                            'buy_price': round(buy[2], 4),
                            'sell_price': round(sell[1], 4),
                            'network': coin,
                            'age': '0с',
                            'transfer_time': '30с',
                            'futures_exchanges': []
                        }
                        signals.append(signal)

    return signals


