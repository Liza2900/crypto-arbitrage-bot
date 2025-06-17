import aiohttp
import os

API_KEY = os.getenv("KUCOIN_API_KEY")
API_SECRET = os.getenv("KUCOIN_API_SECRET")
API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")
BASE_URL = "https://api.kucoin.com"

async def get_prices():
    url = f"{BASE_URL}/api/v1/market/allTickers"
    headers = {
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            if "data" not in data or "ticker" not in data["data"]:
                return {}

            result = {}
            for ticker in data["data"]["ticker"]:
                symbol = ticker["symbol"]
                if symbol.endswith("-USDT"):
                    coin = symbol.replace("-USDT", "")
                    try:
                        price = float(ticker["last"])
                        result[coin] = price
                    except:
                        continue
            return result
