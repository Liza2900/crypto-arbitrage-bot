import httpx
import logging

logger = logging.getLogger(__name__)

async def get_mexc_withdraw_info():
    url = "https://www.mexc.com/open/api/v2/asset/coin/list"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            result = {}
            for coin in data.get("data", []):
                symbol = coin.get("currency")
                chains = coin.get("chains", [])
                network_info = []
                for chain in chains:
                    network_info.append({
                        "network": chain.get("chain"),
                        "withdraw_enabled": chain.get("is_withdraw_enabled"),
                        "withdraw_fee": float(chain.get("withdraw_fee", 0)),
                        "min_withdraw": float(chain.get("min_withdraw_amount", 0))
                    })
                result[symbol] = network_info
            return result

    except Exception as e:
        logger.warning(f"Помилка при отриманні даних з MEXC: {e}")
        return {}
