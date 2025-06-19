import httpx
import os

KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")

headers = {
    "KC-API-KEY": KUCOIN_API_KEY,
    "KC-API-SIGN": "",  # підпис додається динамічно при потребі
    "KC-API-TIMESTAMP": "",
    "KC-API-PASSPHRASE": KUCOIN_API_PASSPHRASE,
    "KC-API-KEY-VERSION": "2"
}

# Проксі з авторизацією (Хорватія)
proxy_url = "http://scomriff:di4xopqednmn@207.244.217.165:6712"

async def get_kucoin_withdraw_info(symbol: str) -> dict:
    """
    Отримує інформацію про вивід монети з KuCoin через API, використовуючи проксі.
    """
    try:
        url = f"https://api.kucoin.com/api/v1/withdrawals/quotas?currency={symbol}"

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
