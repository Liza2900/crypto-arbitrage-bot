import aiohttp
import hmac
import hashlib
import time
import os
import base64

COINEX_API_KEY = os.getenv("COINEX_API_KEY")
COINEX_API_SECRET = os.getenv("COINEX_API_SECRET")

BASE_URL = "https://api.coinex.com/v1"

async def get_coinex_prices():
    url = f"{BASE_URL}/market/ticker/all"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            result = {}
            for symbol, info in data.get("data", {}).items():
                if symbol.endswith("USDT") and float(info.get("ticker", {}).get("last", 0)) < 15:
                    result[symbol.replace("USDT", "")] = {
                        "price": float(info["ticker"]["last"]),
                        "volume": float(info["ticker"]["vol"])
                    }
            return result

async def get_coinex_withdraw_fee(coin):
    url = f"{BASE_URL}/common/asset/config"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            chains = data.get("data", {}).get(coin.upper(), {}).get("withdrawal_limit", {})
            if not chains:
                return None, None, None

            # Вибрати мережу з найменшою комісією
            best = min(chains.items(), key=lambda x: float(x[1]["withdraw_tx_fee"]))
            return float(best[1]["withdraw_tx_fee"]), best[0], best[1].get("estimated_arrival_time", "N/A")

EXCHANGE = {
    "name": "CoinEx",
    "get_prices": get_coinex_prices,
    "get_withdraw_info": get_coinex_withdraw_fee
}
