import aiohttp
import os
import hmac
import base64
import time
import hashlib

OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_API_SECRET = os.getenv("OKX_API_SECRET")
OKX_API_PASSPHRASE = os.getenv("OKX_API_PASSPHRASE")
BASE_URL = "https://www.okx.com"

headers = {
    "Content-Type": "application/json",
    "OK-ACCESS-KEY": OKX_API_KEY,
    "OK-ACCESS-PASSPHRASE": OKX_API_PASSPHRASE,
}

def sign_request(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(bytes(OKX_API_SECRET, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod=hashlib.sha256)
    d = mac.digest()
    return base64.b64encode(d).decode("utf-8")

async def get_spot_tickers():
    url = f"{BASE_URL}/api/v5/market/tickers?instType=SPOT"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            result = {}
            for item in data.get("data", []):
                symbol = item["instId"].replace("-USDT", "")
                if "USDT" in item["instId"]:
                    result[symbol] = float(item["last"])
            return result

async def get_withdrawal_fees():
    path = "/api/v5/asset/currencies"
    timestamp = str(time.time())
    headers.update({
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-SIGN": sign_request(timestamp, "GET", path),
    })
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(BASE_URL + path) as resp:
            data = await resp.json()
            fees = {}
            for coin in data.get("data", []):
                symbol = coin["ccy"]
                if coin.get("chain") and coin.get("minFee"):
                    chain = coin["chain"]
                    fee = coin["minFee"]
                    key = f"{symbol}_{chain}"
                    fees[key] = fee
            return fees
