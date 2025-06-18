import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BITGET_API_KEY = os.getenv("BITGET_API_KEY")
BITGET_API_SECRET = os.getenv("BITGET_API_SECRET")
BITGET_API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

async def get_bitget_withdraw_info(symbol: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.bitget.com/api/spot/v1/public/currencies"
            )
            data = response.json()

            if data.get("code") != "00000":
                raise Exception("Bitget API error")

            networks = []
            fees = {}
            can_withdraw = False
            
            for item in data.get("data", []):
                if item.get("coin") != symbol.upper():
                    continue
                
                chain = item.get("chain", "")
                if not chain:
                    continue
                
                networks.append(chain)
                fees[chain] = float(item.get("withdrawFee", 0))
                if item.get("withdrawable") == True:
                    can_withdraw = True

            return {
                "networks": networks,
                "fees": fees,
                "can_withdraw": can_withdraw,
                "estimated_time": "~10-20 min"
            }
    except Exception as e:
        print(f"Bitget withdraw info error: {e}")
        return {
            "networks": [],
            "fees": {},
            "can_withdraw": False,
            "estimated_time": None
        }
