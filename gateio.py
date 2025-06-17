import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GATEIO_API_URL = "https://api.gate.io/api2/1/tickers"

async def get_prices():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(GATEIO_API_URL)
            data = response.json()
            result = {}
            for symbol, info in data.items():
                if symbol.endswith("_usdt"):
                    coin = symbol.replace("_usdt", "").upper()
                    price = float(info['last'])
                    result[coin] = price
            return result
    except Exception as e:
        print("Gate.io error:", e)
        return {}
