import httpx
import os
import time
import hmac
import hashlib
import base64

KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")

proxy_url = "http://scomriff:di4xopqednmn@207.244.217.165:6712"

def sign_request(timestamp: str, method: str, endpoint: str, body: str = "") -> dict:
    """
    Створює заголовки з підписом для KuCoin API.
    """
    str_to_sign = f"{timestamp}{method.upper()}{endpoint}{body}"
    signature = base64.b64encode(
        hmac.new(
            KUCOIN_API_SECRET.encode("utf-8"),
            str_to_sign.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode()

    passphrase = base64.b64encode(
        hmac.new(
            KUCOIN_API_SECRET.encode("utf-8"),
            KUCOIN_API_PASSPHRASE.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode()

    return {
        "KC-API-KEY": KUCOIN_API_KEY,
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": timestamp,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json"
    }

async def get_kucoin_withdraw_info(symbol: str) -> dict:
    """
    Отримує інфо про вивід з KuCoin через API з коректними підписами.
    """
    try:
        method = "GET"
        endpoint = f"/api/v1/withdrawals/quotas?currency={symbol}"
        url = f"https://api.kucoin.com{endpoint}"

        timestamp = str(int(time.time() * 1000))
        headers = sign_request(timestamp, method, endpoint)

        async with httpx.AsyncClient(proxies=proxy_url, timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            data = response.json()

        if data.get("code") != "200000":
            print(f"[KuCoin Withdraw Error] {data.get('msg')}")
            return {
                "networks": [],
                "fees": {},
                "can_withdraw": False,
                "estimated_time": None
            }

        quota = data["data"]
        chain = quota.get("chain", "unknown")
        fee = float(quota.get("withdrawMinFee", 0))

        return {
            "networks": [chain],
            "fees": {chain: fee},
            "can_withdraw": quota.get("isWithdrawEnabled", False),
            "estimated_time": "~10-30 хв"
        }

    except Exception as e:
        print(f"[KuCoin Withdraw Error] {e}")
        return {
            "networks": [],
            "fees": {},
            "can_withdraw": False,
            "estimated_time": None
        }

