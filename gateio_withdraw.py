import httpx
import os

GATEIO_API_KEY = os.getenv("GATEIO_API_KEY")
GATEIO_API_SECRET = os.getenv("GATEIO_API_SECRET")
GATEIO_API_BASE = "https://api.gateio.ws/api/v4"

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "KEY": GATEIO_API_KEY,
    "SIGN": ""
    # SIGN не потрібен для публічного GET-запиту /wallet/withdraw_status
}

async def get_gateio_withdraw_info(symbol):
    try:
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            url = f"{GATEIO_API_BASE}/wallet/withdraw_status"
            resp = await client.get(url, headers=HEADERS)
            resp.raise_for_status()
            data = resp.json()

        for coin in data:
            if coin["currency"] == symbol:
                return {
                    "can_withdraw": coin["withdrawable"],
                    "networks": [coin["chain"]] if "chain" in coin else [],
                    "fees": {coin["chain"]: float(coin["withdraw_fix"])} if "chain" in coin else {},
                    "estimated_time": "-"
                }
        return {
            "can_withdraw": False,
            "networks": [],
            "fees": {},
            "estimated_time": None
        }
    except Exception as e:
        print(f"[Gate.io Withdraw Error] {e}")
        return {
            "can_withdraw": False,
            "networks": [],
            "fees": {},
            "estimated_time": None
        }
