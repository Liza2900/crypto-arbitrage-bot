import aiohttp
import os

MEXC_BASE_URL = "https://api.mexc.com"

async def get_mexc_prices():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{MEXC_BASE_URL}/api/v3/ticker/bookTicker") as resp:
            data = await resp.json()
            return {
                item["symbol"]: {
                    "bid": float(item["bidPrice"]),
                    "ask": float(item["askPrice"])
                }
                for item in data if item["symbol"].endswith("USDT")
            }

# Приклад: отримати комісію виводу
async def get_mexc_withdraw_fees(symbol: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{MEXC_BASE_URL}/api/v3/capital/config/getall") as resp:
            data = await resp.json()
            for item in data:
                if item["coin"] == symbol:
                    return item["networkList"]
    return []
