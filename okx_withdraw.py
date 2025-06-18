import aiohttp

BASE_URL = "https://www.okx.com"

async def get_okx_withdraw_info():
    """
    Повертає словник:
    {
        'USDT': {
            'networks': [
                {
                    'chain': 'TRC20',
                    'is_withdrawable': True,
                    'fee': 1.0,
                    'min_withdraw': 10.0
                },
                ...
            ]
        },
        ...
    }
    """
    url = f"{BASE_URL}/api/v5/asset/currencies"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            result = {}

            for item in data.get("data", []):
                currency = item["ccy"]
                chain = item.get("chain", "")
                can_withdraw = item.get("canWd", "false") == "true"
                fee = float(item.get("minFee", 0))
                min_wd = float(item.get("minWd", 0))

                if currency not in result:
                    result[currency] = {"networks": []}

                result[currency]["networks"].append({
                    "chain": chain,
                    "is_withdrawable": can_withdraw,
                    "fee": fee,
                    "min_withdraw": min_wd,
                })

            return result
