import os
import httpx
from dotenv import load_dotenv
import hashlib
import hmac
import time

load_dotenv()

BINGX_API_KEY = os.getenv("BINGX_API_KEY")
BINGX_API_SECRET = os.getenv("BINGX_API_SECRET")

BASE_URL = "https://open-api.bingx.com"

def sign(params: dict) -> str:
    query_string = "&".join(f"{key}={value}" for key, value in sorted(params.items()))
    return hmac.new(
        BINGX_API_SECRET.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

async def get_bingx_withdraw_info(symbol: str) -> dict:
    """
    Отримує список доступних мереж для виводу, їхні комісії та статус.
    """
    try:
        timestamp = str(int(time.time() * 1000))
        params = {
            "timestamp": timestamp,
            "recvWindow": "5000"
        }
        headers = {
            "X-BX-APIKEY": BINGX_API_KEY
        }

        params["signature"] = sign(params)

        url = f"{BASE_URL}/openApi/asset/v1/withdraw/currencyList"

        response = httpx.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        networks = []
        fees = {}
        can_withdraw = False

        if data.get("code") == 0:
            for asset in data["data"]:
                if asset["coin"] == symbol.upper():
                    for chain in asset.get("networkList", []):
                        network = chain.get("network")
                        fee = float(chain.get("withdrawFee", 0))
                        withdraw_enabled = chain.get("withdrawEnable", False)
                        if withdraw_enabled:
                            networks.append(network)
                            fees[network] = fee
                            can_withdraw = True

        return {
            "networks": networks,
            "fees": fees,
            "can_withdraw": can_withdraw,
            "estimated_time": "~10 хв"
        }

    except Exception as e:
        print(f"BingX withdraw fetch error: {e}")
        return {
            "networks": [],
            "fees": {},
            "can_withdraw": False,
            "estimated_time": None
        }
