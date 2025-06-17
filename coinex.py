import httpx

COINEX_API_URL = "https://api.coinex.com/v1/market/ticker/all"

async def get_prices():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(COINEX_API_URL)
            data = response.json()
            result = {}
            ticker_data = data.get("data", {}).get("ticker", {})
            for pair, info in ticker_data.items():
                if pair.endswith("USDT"):
                    coin = pair.replace("USDT", "").replace("_", "")
                    result[coin.upper()] = float(info.get("last", 0))
            return result
    except Exception as e:
        print("CoinEx error:", e)
        return {}
