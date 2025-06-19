from kucoin import get_prices as get_kucoin_prices
from mexc import get_prices as get_mexc_prices
from bitget import get_prices as get_bitget_prices
from okx import get_prices as get_okx_prices
from bingx import get_prices as get_bingx_prices
from gateio import get_prices as get_gateio_prices
from coinex import get_prices as get_coinex_prices

from withdraw import get_withdraw_info
import logging

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
            logging.warning(f"Помилка при отриманні цін з {name}: {e}")
            prices[name] = {}
    return prices

async def find_arbitrage_opportunities(prices, filters):
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

                    spread = ((sell_price - buy_price) / buy_price) * 100
                    if spread <= 0:
                        continue

                    profit = (spread / 100) * filters["budget"]

                    print(f"{coin} | {buy_exchange} -> {sell_exchange} | Buy: {buy_price:.4f} Sell: {sell_price:.4f} Spread: {spread:.2f}% Profit: {profit:.2f}$")

                    # Тимчасово прибираємо фільтр на min_profit_usd

                    # Отримати інфу про вивід
                    withdraw_info = await get_withdraw_info(buy_exchange, coin)
                    if not withdraw_info.get("can_withdraw", False):
                        continue

                    networks = ", ".join(withdraw_info.get("networks", [])) or "невідомо"
                    fees = withdraw_info.get("fees", {})
                    fees_str = ", ".join(f"{k}: {v}" for k, v in fees.items()) or "-"
                    time_str = withdraw_info.get("estimated_time") or "-"

                    text = f"{coin}: {buy_exchange} → {sell_exchange}\n"
                    text += f"Ціна купівлі: {buy_price:.4f}$, Продажу: {sell_price:.4f}$\n"
                    text += f"📈 Профіт: {spread:.2f}% ≈ {profit:.2f}$\n"
                    text += f"🌐 Мережі: {networks}\n"
                    text += f"💸 Комісії: {fees_str}\n"
                    text += f"⏱️ Час переказу: {time_str}"
                    opportunities.append(text)
    return opportunities
