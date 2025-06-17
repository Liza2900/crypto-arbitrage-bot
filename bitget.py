import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BITGET_API_URL = "https://api.bitget.com/api/spot/v1/market/tickers"

async def get_prices():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BITGET_API_URL)
            data = response.json()
            result = {}
            for item in data.get("data", []):
                symbol = item.get("symbol")  # наприклад: BTCUSDT
                if symbol.endswith("USDT"):
                    coin = symbol.replace("USDT", "")
                    result[coin] = float(item.get("lastPr", 0))
            return result
    except Exception as e:
        print("Bitget error:", e)
        return {}
