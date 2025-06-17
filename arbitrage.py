from kucoin import get_prices as get_kucoin_prices
from mexc import get_prices as get_mexc_prices
from bitget import get_prices as get_bitget_prices
from okx import get_prices as get_okx_prices
from bingx import get_prices as get_bingx_prices
from gateio import get_prices as get_gateio_prices
from coinex import get_prices as get_coinex_prices

EXCHANGES = {
    "KuCoin": get_kucoin_prices,
    "MEXC": get_mexc_prices,
    "Bitget": get_bitget_prices,
    "OKX": get_okx_prices,
    "BingX": get_bingx_prices,
    "Gate.io": get_gateio_prices,
    "CoinEx": get_coinex_prices
}

async def fetch_prices_from_exchanges(filters):
    prices = {}
    for name, func in EXCHANGES.items():
        try:
            prices[name] = await func()
        except Exception as e:
            prices[name] = {}
    return prices

def find_arbitrage_opportunities(prices, filters):
    opportunities = []
    for buy_exchange, buy_prices in prices.items():
        for sell_exchange, sell_prices in prices.items():
            if buy_exchange == sell_exchange:
                continue
            for coin in buy_prices:
                if coin in sell_prices:
                    buy_price = buy_prices[coin]
                    sell_price = sell_prices[coin]
                    spread = ((sell_price - buy_price) / buy_price) * 100
                    if spread <= 0:
                        continue
                    profit = (spread / 100) * filters["budget"]
                    if profit >= filters.get("min_profit_usd", 1.0):
                        text = f"{coin}: {buy_exchange} → {sell_exchange}
Ціна купівлі: {buy_price:.4f}$, Продажу: {sell_price:.4f}$
📈 Профіт: {spread:.2f}% ≈ {profit:.2f}$"
                        opportunities.append(text)
    return opportunities
