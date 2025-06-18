import aiohttp

async def get_withdraw_info_kucoin(symbol: str) -> dict:
    """
    Повертає інформацію про можливість виводу USDT за символом (наприклад, "USDT").
    """
    async with aiohttp.ClientSession() as session:
        resp = await session.get("https://api.kucoin.com/api/v1/currencies")
        data = await resp.json()
        for item in data.get("data", []):
            if item["currency"] == symbol:
                # Припустимо, беремо мережу TRC20
                chains = item.get("chains", [])
                for chain in chains:
                    if chain["network"] == "TRC20":
                        return {
                            "network": "TRC20",
                            "withdraw_fee": float(chain["withdrawMinFee"]) if chain.get("withdrawMinFee") else None,
                            "is_withdrawable": chain.get("isWithdrawEnabled", False),
                            "estimated_time_min": 5  # Можна замінити реальним API полем
                        }
        # Якщо немає потрібної мережі або валюти
        return {
            "network": None,
            "withdraw_fee": None,
            "is_withdrawable": False,
            "estimated_time_min": None
        }
