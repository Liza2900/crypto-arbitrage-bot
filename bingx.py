import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BINGX_API_URL = "https://open-api.bingx.com/openApi/spot/v1/ticker/24hr"

async def get_prices():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BINGX_API_URL)
            data = response.json()
            result = {}
            for item in data.get("data", []):
                symbol = item.get("symbol")  # наприклад: BTC-USDT
                if symbol and symbol.endswith("USDT"):
                    coin = symbol.replace("USDT", "").replace("-", "").replace("/", "")
                    result[coin] = float(item.get("lastPrice", 0))
            return result
    except Exception as e:
        print("BingX error:", e)
        return {}
