import time
import hmac
import hashlib
import httpx
from typing import Dict, List

API_KEY = "YOUR_GATE_API_KEY"
API_SECRET = "YOUR_GATE_API_SECRET"
BASE_URL = "https://api.gate.io"

headers_template = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "KEY": API_KEY
}

def sign_request(method: str, path: str, body: str, timestamp: str) -> str:
    message = f"{method.upper()}\n{path}\n{timestamp}\n{body}"
    signature = hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha512).hexdigest()
    return signature

async def get_withdraw_info(currency: str) -> Dict:
    timestamp = str(int(time.time()))
    method = "GET"
    path = f"/api/v4/wallet/withdraw_status?currency={currency}"
    body = ""

    signature = sign_request(method, path, body, timestamp)

    headers = headers_template.copy()
    headers["Timestamp"] = timestamp
    headers["SIGN"] = signature

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        try:
            response = await client.get(path, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Gate.io withdraw error for {currency}: {e}")
            return {}

async def get_all_gateio_withdraw_info(currencies: List[str]) -> Dict[str, Dict]:
    result = {}
    for currency in currencies:
        info = await get_withdraw_info(currency)
        if info:
            result[currency] = info
    return result
