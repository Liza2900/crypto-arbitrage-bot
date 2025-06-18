import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GATEIO_API_KEY = os.getenv("GATEIO_API_KEY")
GATEIO_API_SECRET = os.getenv("GATEIO_API_SECRET")

BASE_URL = "https://api.gate.io/api/v4"

async def get_gateio_withdraw_info(symbol: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/wallet/withdraw_status")
            data = response.json()

        networks = []
        fees = {}

        for item in data:
            if item["currency"] == symbol:
                chain = item.get("chain", "")
                fee = float(item.get("withdraw_fix", 0))
                if chain:
                    networks.append(chain)
                    fees[chain] = fee

        return {
            "networks": networks,
            "fees": fees,
            "can_withdraw": len(networks) > 0,
            "estimated_time": "~10-30 min"
        }

    except Exception as e:
        print(f"Gate.io withdraw error: {e}")
        return {
            "networks": [],
            "fees": {},
            "can_withdraw": False,
            "estimated_time": None
        }
