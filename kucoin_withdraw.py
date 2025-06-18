import os
import time
import base64
import hmac
import hashlib
import httpx

KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")

def _get_kucoin_signature(timestamp, method, endpoint, body=""):
    str_to_sign = f"{timestamp}{method}{endpoint}{body}"
    signature = base64.b64encode(
        hmac.new(KUCOIN_API_SECRET.encode("utf-8"), str_to_sign.encode("utf-8"), hashlib.sha256).digest()
    ).decode()
    return signature

def _get_kucoin_passphrase():
    return base64.b64encode(
        hmac.new(KUCOIN_API_SECRET.encode("utf-8"), KUCOIN_API_PASSPHRASE.encode("utf-8"), hashlib.sha256).digest()
    ).decode()

async def get_kucoin_withdraw_info(symbol: str) -> dict:
    try:
        timestamp = str(int(time.time() * 1000))
        endpoint = f"/api/v1/withdrawals/quotas?currency={symbol}"
        signature = _get_kucoin_signature(timestamp, "GET", endpoint)
        passphrase = _get_kucoin_passphrase()

        headers = {
            "KC-API-KEY": KUCOIN_API_KEY,
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
            "Content-Type": "application/json"
        }

        url = f"https://api.kucoin.com{endpoint}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            data = response.json()

        if data["code"] != "200000":
            raise Exception(data.get("msg", "Unknown error"))

        result = data["data"]
        return {
            "networks": [result["chain"]],
            "fees": {result["chain"]: float(result["withdrawMinFee"])},
            "can_withdraw": result["isWithdrawEnabled"],
            "estimated_time": "~15 min"
        }
    except Exception as e:
        print(f"[KuCoin Withdraw Error] {e}")
        return {
            "networks": [],
            "fees": {},
            "can_withdraw": False,
            "estimated_time": None
        }
