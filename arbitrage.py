import asyncio
from mexc import get_prices as get_mexc_prices
from kucoin import get_prices as get_kucoin_prices
from gateio import get_prices as get_gateio_prices
from okx import get_prices as get_okx_prices
from bingx import get_prices as get_bingx_prices
from bitget import get_prices as get_bitget_prices
from coinex import get_prices as get_coinex_prices

EXCHANGES = {
    "MEXC": get_mexc_prices,
    "KuCoin": get_kucoin_prices,
    "Gate.io": get_gateio_prices,
    "OKX": get_okx_prices,
    "BingX": get_bingx_prices,
    "Bitget": get_bitget_prices,
    "CoinEx": get_coinex_prices,
}

async def fetch_prices_from_exchanges():
    results = await asyncio.gather(*[func() for func in EXCHANGES.values()])
    return dict(zip(EXCHANGES.keys(), results))

def find_arbitrage_opportunities(prices, filters):
    min_volume = filters.get("min_volume", 10)
    min_profit = filters.get("min_profit", 0.8)
    exchanges_buy = filters.get("exchanges_buy", {})
    exchanges_sell = filters.get("exchanges_sell", {})
    budget = filters.get("budget", 100)

    opportunities = []

    for ex1, data1 in prices.items():
        for ex2, data2 in prices.items():
            if ex1 == ex2 or not exchanges_buy.get(ex1) or not exchanges_sell.get(ex2):
                continue

            common_coins = set(data1.keys()) & set(data2.keys())

            for coin in common_coins:
                buy_price = data1[coin]["price"]
                sell_price = data2[coin]["price"]

                if buy_price <= 0 or sell_price <= 0:
                    continue

                spread = round((sell_price - buy_price) / buy_price * 100, 2)
                volume = min(data1[coin].get("volume", 0), data2[coin].get("volume", 0)) * buy_price

                if spread >= min_profit and volume >= min_volume:
                    opportunities.append({
                        "coin": coin,
                        "buy_exchange": ex1,
                        "sell_exchange": ex2,
                        "buy_price": round(buy_price, 4),
                        "sell_price": round(sell_price, 4),
                        "spread": spread,
                        "volume": round(volume, 2),
                        "withdraw_fee": data1[coin].get("withdraw_fee", "?"),
                        "network": data1[coin].get("network", "?"),
                        "transfer_time": data1[coin].get("transfer_time", "?")
                    })

    sorted_opps = sorted(opportunities, key=lambda x: x["spread"], reverse=True)
    return sorted_opps
