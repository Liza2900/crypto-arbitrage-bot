import os
import httpx
from dotenv import load_dotenv

load_dotenv()

OKX_API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SPOT"

async def get_prices():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OKX_API_URL)
            data = response.json()
            result = {}
            for item in data['data']:
                inst_id = item['instId']  # Наприклад: BTC-USDT
                if inst_id.endswith("USDT"):
                    coin = inst_id.replace("-USDT", "")
                    result[coin] = float(item['last'])
            return result
    except Exception as e:
        print("OKX error:", e)
        return {}
