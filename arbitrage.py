import random

def get_mock_arbitrage_opportunities(user_filters):
    """
    Генерує випадкові арбітражні можливості згідно з активними фільтрами користувача.
    """
    opportunities = []

    exchanges_buy = [ex for ex, enabled in user_filters['exchanges_buy'].items() if enabled]
    exchanges_sell = [ex for ex, enabled in user_filters['exchanges_sell'].items() if enabled]

    if not exchanges_buy or not exchanges_sell:
        return []

    for _ in range(5):
        buy_exchange = random.choice(exchanges_buy)
        sell_exchange = random.choice(exchanges_sell)
        if buy_exchange == sell_exchange:
            continue

        profit = round(random.uniform(0.5, 3.0), 2)
        volume = round(random.uniform(50, 500), 2)

        if profit < user_filters['min_profit'] or volume < user_filters['min_volume']:
            continue

        opportunity = {
            "symbol": random.choice(["TRX/USDT", "XRP/USDT", "DOGE/USDT"]),
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "buy_price": round(random.uniform(0.02, 0.2), 5),
            "sell_price": round(random.uniform(0.03, 0.22), 5),
            "profit": profit,
            "volume": volume,
            "network": random.choice(["TRC20", "ERC20", "BEP20"]),
            "transfer_time": random.choice(["2 хв", "5 хв", "12 хв"]),
            "lifespan": random.choice(["15 сек", "1 хв", "3 хв"]),
            "hedge": random.choice([["Bybit"], ["Gate.io", "KuCoin"], []])
        }

        opportunities.append(opportunity)

    return opportunities

def format_opportunity_message(op):
    """
    Формує повідомлення у стилі арбітражного сигналу.
    """
    return f"""
💰 {op['symbol']}
Биржи: {op['buy_exchange']} → {op['sell_exchange']}
Профит: {op['profit']}%
Объём: {op['volume']}$
Купить на: [{op['buy_exchange']}]({generate_exchange_link(op['buy_exchange'], op['symbol'])}) по цене *{op['buy_price']}*
Продать на: [{op['sell_exchange']}]({generate_exchange_link(op['sell_exchange'], op['symbol'])}) по цене *{op['sell_price']}*
Сеть: {op['network']}
Время жизни: {op['lifespan']}
Трансфер: {op['transfer_time']}
Хеджирование: {', '.join(op['hedge']) if op['hedge'] else 'Немає'}
    """

def generate_exchange_link(exchange, symbol):
    """
    Генерує посилання на торгову пару біржі.
    """
    base_urls = {
        "MEXC": "https://www.mexc.com/exchange",
        "KuCoin": "https://www.kucoin.com/trade",
        "Bitget": "https://www.bitget.com/spot",
        "OKX": "https://www.okx.com/trade-spot",
        "BingX": "https://bingx.com/en-us/spot",
        "Gate.io": "https://www.gate.io/trade",
        "Bybit": "https://www.bybit.com/trade/spot"
    }
    if exchange in base_urls:
        return f"{base_urls[exchange]}/{symbol.replace('/', '_')}"
    return "#"
