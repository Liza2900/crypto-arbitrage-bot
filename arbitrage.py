import ccxt
import asyncio

# Біржі для арбітражу
EXCHANGES = {
    "KuCoin": ccxt.kucoin(),
    "MEXC": ccxt.mexc(),
    "OKX": ccxt.okx(),
    "Bitget": ccxt.bitget(),
    "BingX": ccxt.bingx(),
    "Gate.io": ccxt.gateio(),
    "Bybit": ccxt.bybit(),
}

# Комісії за вивід по біржах (умовні приклади, краще оновлювати динамічно)
WITHDRAW_FEES = {
    "DOGE": {"KuCoin": 5, "MEXC": 4, "OKX": 5, "Bitget": 3, "BingX": 2, "Gate.io": 5, "Bybit": 6},
    "XRP": {"KuCoin": 0.25, "MEXC": 0.2, "OKX": 0.25, "Bitget": 0.15, "BingX": 0.1, "Gate.io": 0.25, "Bybit": 0.3},
    "SOL": {"KuCoin": 0.01, "MEXC": 0.01, "OKX": 0.01, "Bitget": 0.005, "BingX": 0.005, "Gate.io": 0.01, "Bybit": 0.01},
    "ALGO": {"KuCoin": 0.01, "MEXC": 0.01, "OKX": 0.01, "Bitget": 0.01, "BingX": 0.01, "Gate.io": 0.01, "Bybit": 0.01},
    "TRX": {"KuCoin": 1, "MEXC": 1, "OKX": 1, "Bitget": 1, "BingX": 1, "Gate.io": 1, "Bybit": 1},
    "ARB": {"KuCoin": 0.1, "MEXC": 0.1, "OKX": 0.1, "Bitget": 0.1, "BingX": 0.1, "Gate.io": 0.1, "Bybit": 0.1},
    "LINK": {"KuCoin": 0.3, "MEXC": 0.3, "OKX": 0.3, "Bitget": 0.2, "BingX": 0.2, "Gate.io": 0.3, "Bybit": 0.35},
}

# Перелік монет (без BTC та ETH)
COINS = ["DOGE", "XRP", "SOL", "ALGO", "TRX", "ARB", "LINK"]

# Асинхронне отримання цін з усіх бірж
async def fetch_prices_from_exchanges():
    prices = {}
    for name, exchange in EXCHANGES.items():
        prices[name] = {}
        try:
            markets = exchange.load_markets()
        except Exception as e:
            print(f"⚠️ Не вдалося завантажити ринки для {name}: {e}")
            continue

        for coin in COINS:
            pair = f"{coin}/USDT"
            if pair not in markets:
                continue

            try:
                ticker = exchange.fetch_ticker(pair)
                orderbook = exchange.fetch_order_book(pair)
                price = ticker['ask']
                volume = orderbook['asks'][0][1] if orderbook['asks'] else 0
                withdraw_fee = WITHDRAW_FEES.get(coin, {}).get(name, 0.5)
                prices[name][coin] = {
                    "price": int(price),
                    "volume": round(volume * price, 2),
                    "withdraw_fee": withdraw_fee,
                    "network": "TRC20",
                    "is_withdrawable": True,
                    "transfer_time": f"{10 + hash(coin + name) % 20} min"
                }
            except Exception as e:
                print(f"❌ Помилка отримання {pair} з {name}: {e}")
    return prices

# Пошук можливостей арбітражу
def find_arbitrage_opportunities(prices, filters):
    opportunities = []
    shown_pairs = set()
    for coin in COINS:
        for buy_ex in EXCHANGES:
            for sell_ex in EXCHANGES:
                if buy_ex == sell_ex:
                    continue
                if not filters['exchanges_buy'].get(buy_ex, True):
                    continue
                if not filters['exchanges_sell'].get(sell_ex, True):
                    continue

                pair_id = (coin, buy_ex, sell_ex)
                if pair_id in shown_pairs:
                    continue
                shown_pairs.add(pair_id)

                buy_data = prices.get(buy_ex, {}).get(coin)
                sell_data = prices.get(sell_ex, {}).get(coin)

                if not buy_data or not sell_data:
                    continue

                spread = ((sell_data['price'] - buy_data['price']) / buy_data['price']) * 100
                if spread >= filters['min_profit']:
                    volume = min(filters['budget'], buy_data['volume'])
                    if volume < 5:
                        continue

                    opportunities.append({
                        "coin": coin,
                        "buy_exchange": buy_ex,
                        "sell_exchange": sell_ex,
                        "buy_price": buy_data['price'],
                        "sell_price": sell_data['price'],
                        "spread": round(spread, 2),
                        "volume": round(volume, 2),
                        "network": buy_data['network'],
                        "withdraw_fee": buy_data['withdraw_fee'],
                        "is_withdrawable": buy_data['is_withdrawable'],
                        "transfer_time": buy_data['transfer_time']
                    })
    return sorted(opportunities, key=lambda x: -x['spread'])[:2]  # топ-2 арбітражі

