import httpx

API_URL = "https://api.mexc.com/api/v3/ticker/bookTicker"

async def get_prices():
    prices = {}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(API_URL)
            data = resp.json()

        for item in data:
            symbol = item.get("symbol")
            bid = item.get("bidPrice")
            ask = item.get("askPrice")

            if not symbol or not bid or not ask:
                continue

            if symbol.endswith("USDT") and not symbol.endswith("3SUSDT") and not symbol.endswith("3LUSDT"):
                coin = symbol.replace("USDT", "")
                try:
                    buy_price = float(ask)
                    sell_price = float(bid)
                    avg_price = (buy_price + sell_price) / 2
                    prices[coin] = avg_price
                except (ValueError, TypeError):
                    continue
    except Exception as e:
        import logging
        logging.warning(f"Помилка при отриманні цін з MEXC: {e}")
    return prices
