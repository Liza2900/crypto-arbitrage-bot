import os
import time
import hmac
import hashlib
import httpx
from dotenv import load_dotenv

load_dotenv()

COINEX_API_KEY = os.getenv("COINEX_API_KEY")
COINEX_API_SECRET = os.getenv("COINEX_API_SECRET")

BASE_URL = "https://api.coinex.com/v1"

def make_signature(tonce: str, params: dict) -> str:
    sorted_params = sorted(params.items())
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    to_sign = f"{query_string}&access_id={COINEX_API_KEY}&tonce={tonce}"
    signature = hmac.new(
        COINEX_API_SECRET.encode("utf-8"),
        to_sign.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()
    return signature

def get_coinex_withdraw_info(symbol: str) -> dict:
    """
    Отримує доступні мережі, комісії, можливість виводу з CoinEx.
    """
    try:
        tonce = str(int(time.time() * 1000))
        headers = {
            "Authorization": COINEX_API_KEY
        }

        params = {
            "tonce": tonce,
            "access_id": COINEX_API_KEY
        }

        signature = make_signature(tonce, params)
        params["signature"] = signature

        response = httpx.get(f"{BASE_URL}/common/asset/config", params=params, headers=headers, timeout=10)
        data = response.json()

        networks = []
        fees = {}
        can_withdraw = False

        if data.get("code") == 0:
            asset_data = data.get("data", {})
            for full_symbol, asset_info in asset_data.items():
                if asset_info["asset"] == symbol.upper():
                    for chain_info in asset_info.get("chains", []):
                        chain = chain_info.get("chain")
                        withdraw_enabled = chain_info.get("can_withdraw", False)
                        fee = float(chain_info.get("withdraw_tx_fee", 0))
                        if withdraw_enabled:
                            networks.append(chain)
                            fees[chain] = fee
                            can_withdraw = True

        return {
            "networks": networks,
            "fees": fees,
            "can_withdraw": can_withdraw,
            "estimated_time": "~15 хв"
        }

    except Exception as e:
        print(f"CoinEx withdraw fetch error: {e}")
        return {
            "networks": [],
            "fees": {},
            "can_withdraw": False,
            "estimated_time": None
        }
