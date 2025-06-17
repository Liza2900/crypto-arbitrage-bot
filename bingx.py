import aiohttp
import os

API_KEY = os.getenv("BINGX_API_KEY")
API_SECRET = os.getenv("BINGX_API_SECRET")

BASE_URL = "https://open-api.bingx.com"

HEADERS = {
    "X-BX-APIKEY": API_KEY
}

async def get_spot_prices():
    """
    Отримує спотові ціни (bid/ask) з BingX
    """
    url = f"{BASE_URL}/openApi/spot/v1/ticker/price"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            data = await response.json()

            if data.get("code") != 0:
                raise Exception(f"BingX error: {data.get('msg')}")

            prices = {}
            for item in data["data"]:
                symbol = item["symbol"]  # Наприклад: "DOGE-USDT"
                price = float(item["price"])
                if "-USDT" in symbol:
                    coin = symbol.replace("-USDT", "")
                    prices[coin] = {
                        "bid": price,   # BingX дає тільки середню ціну, використаємо як bid/ask
                        "ask": price
                    }
            return prices
