from kucoin import get_prices as get_kucoin_prices
from mexc import get_prices as get_mexc_prices
from bitget import get_prices as get_bitget_prices
from okx import get_prices as get_okx_prices
from bingx import get_prices as get_bingx_prices
from gateio import get_prices as get_gateio_prices
from coinex import get_prices as get_coinex_prices

from withdraw import get_withdraw_info

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

                    if buy_price is None or sell_price is None or buy_price == 0:
                        continue

                    # Отримуємо інфу про вивід із біржі покупки
                    withdraw_info = get_withdraw_info(buy_exchange, coin)
                    if not withdraw_info["can_withdraw"]:
                        continue

                    # Вибираємо найменшу комісію
                    min_fee = None
                    best_network = None
                    for net, fee in withdraw_info["fees"].items():
                        if min_fee is None or fee < min_fee:
                            min_fee = fee
                            best_network = net

                    if min_fee is None:
                        continue

                    spread = ((sell_price - buy_price) / buy_price) * 100
                    if spread <= 0:
                        continue

                    gross_profit = (spread / 100) * filters["budget"]
                    net_profit = gross_profit - min_fee

                    if net_profit >= filters.get("min_profit_usd", 1.0):
                        text = (
                            f"{coin}: {buy_exchange} → {sell_exchange}\n"
                            f"Купівля: {buy_price:.4f}$ | Продаж: {sell_price:.4f}$\n"
                            f"Мережа: {best_network} | Комісія: {min_fee:.2f}$\n"
                            f"📈 Профіт: {spread:.2f}% ≈ {net_profit:.2f}$ (після комісії)"
                        )
                        opportunities.append(text)
    return opportunities
