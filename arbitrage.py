import random

EXCHANGES = ["KuCoin", "MEXC", "OKX", "Bitget", "BingX", "Gate.io", "Bybit"]

# Імітація отримання цін з API бірж
async def fetch_prices_from_exchanges():
    coins = ["BTC", "ETH", "XRP", "SOL", "DOGE"]
    prices = {}
    for exchange in EXCHANGES:
        prices[exchange] = {}
        for coin in coins:
            prices[exchange][coin] = {
                "price": round(random.uniform(0.5, 15), 4),
                "volume": round(random.uniform(10, 1000), 2),
                "withdraw_fee": round(random.uniform(0.1, 1.0), 2),
                "network": "TRC20",
                "is_withdrawable": True,
                "transfer_time": f"{random.randint(5, 30)} min"
            }
    return prices

# Пошук можливостей арбітражу
def find_arbitrage_opportunities(prices, filters):
    opportunities = []
    for coin in prices[EXCHANGES[0]]:
        for buy_ex in EXCHANGES:
            for sell_ex in EXCHANGES:
                if buy_ex == sell_ex:
                    continue
                if not filters['exchanges_buy'].get(buy_ex, True):
                    continue
                if not filters['exchanges_sell'].get(sell_ex, True):
                    continue

                buy_data = prices[buy_ex].get(coin)
                sell_data = prices[sell_ex].get(coin)
                if not buy_data or not sell_data:
                    continue

                spread = ((sell_data['price'] - buy_data['price']) / buy_data['price']) * 100
                if spread >= filters['min_profit'] and buy_data['volume'] >= filters['min_volume']:
                    opportunities.append({
                        "coin": coin,
                        "buy_exchange": buy_ex,
                        "sell_exchange": sell_ex,
                        "buy_price": buy_data['price'],
                        "sell_price": sell_data['price'],
                        "spread": round(spread, 2),
                        "volume": buy_data['volume'],
                        "network": buy_data['network'],
                        "withdraw_fee": buy_data['withdraw_fee'],
                        "is_withdrawable": buy_data['is_withdrawable'],
                        "transfer_time": buy_data['transfer_time']
                    })
    return opportunities
