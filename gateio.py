import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.gate.io/api/v4"
API_KEY = os.getenv("GATEIO_API_KEY")
API_SECRET = os.getenv("GATEIO_API_SECRET")

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

async def get_gateio_prices():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/spot/tickers") as resp:
            data = await resp.json()
            prices = {}
            for item in data:
                symbol = item["currency_pair"]
                if symbol.endswith("_USDT"):
                    coin = symbol.replace("_USDT", "")
                    prices[coin] = {
                        "ask": float(item["lowest_ask"]),
                        "bid": float(item["highest_bid"])
                    }
            return prices

async def get_gateio_withdrawal_info(coin: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/wallet/withdraw_status") as resp:
            data = await resp.json()
            for item in data:
                if item["currency"] == coin:
                    return {
                        "fee": float(item["withdraw_fix"]),
                        "network": item.get("name", "Unknown"),
                        "is_withdrawable": item.get("withdrawable", False),
                        "estimated_time": item.get("estimated_arrival_time", "unknown")
                    }
            return None
