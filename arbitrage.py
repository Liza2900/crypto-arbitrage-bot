import aiohttp

# Біржі
EXCHANGES = ["KuCoin", "MEXC", "Bitget", "OKX", "BingX", "Gate.io", "Bybit"]

# Псевдо-реалізація функції отримання ціни з API біржі (заглушка)
async def fetch_price(session, exchange, symbol):
    url = f"https://api.{exchange.lower()}.com/api/v1/price?symbol={symbol}"
    try:
        async with session.get(url, timeout=10) as resp:
            data = await resp.json()
            # Тут залежить від структури відповіді конкретної біржі
            return float(data.get("price"))
    except:
        return None

# Основна функція пошуку арбітражних можливостей
async def find_arbitrage_opportunities(filters):
    symbols = ["SOL/USDT", "XRP/USDT", "DOGE/USDT"]  # Тимчасово жорстко задані
    opportunities = []

    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            prices = {}
            for ex in EXCHANGES:
                price = await fetch_price(session, ex, symbol.replace("/", ""))
                if price:
                    prices[ex] = price

            for ex_buy in filters["exchanges_buy"]:
                if not filters["exchanges_buy"][ex_buy] or ex_buy not in prices:
                    continue
                for ex_sell in filters["exchanges_sell"]:
                    if not filters["exchanges_sell"][ex_sell] or ex_sell not in prices:
                        continue
                    buy_price = prices[ex_buy]
                    sell_price = prices[ex_sell]
                    profit = (sell_price - buy_price) / buy_price * 100
                    if profit >= filters["min_profit"]:
                        opportunities.append({
                            "symbol": symbol,
                            "buy_exchange": ex_buy,
                            "sell_exchange": ex_sell,
                            "buy_price": round(buy_price, 4),
                            "sell_price": round(sell_price, 4),
                            "profit": round(profit, 2),
                        })

    return sorted(opportunities, key=lambda x: x["profit"], reverse=True)
