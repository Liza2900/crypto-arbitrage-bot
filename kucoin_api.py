from kucoin.client import Client
import os

KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")

client = Client(KUCOIN_API_KEY, KUCOIN_API_SECRET, KUCOIN_API_PASSPHRASE)

async def get_kucoin_prices():
    result = {}
    try:
        tickers = client.get_all_tickers()["ticker"]
        for t in tickers:
            symbol = t["symbol"]
            if symbol.endswith("-USDT"):
                coin = symbol.replace("-USDT", "")
                result[coin] = {
                    "price": float(t["last"]),
                    "volume": float(t["volValue"])  # USDT volume
                }
    except Exception as e:
        print("KuCoin API error:", e)
    return result
