def generate_arbitrage_signals(filters):
    # Це фейкові дані для демонстрації
    signals = []

    example_signal = {
        'coin': 'SOL',
        'buy_exchange': 'MEXC',
        'sell_exchange': 'KuCoin',
        'spread': 1.42,
        'volume': 290,
        'buy_price': 144.12,
        'sell_price': 146.17,
        'network': 'SOL',
        'age': '25с',
        'transfer_time': '30с',
        'futures_exchanges': ['Bybit', 'Gate.io', 'OKX']
    }

    # Фільтрація за умовами
    if (
        example_signal['spread'] >= filters['min_profit']
        and example_signal['volume'] >= filters['min_volume']
        and filters['exchanges_buy'].get(example_signal['buy_exchange'], False)
        and filters['exchanges_sell'].get(example_signal['sell_exchange'], False)
    ):
        signals.append(example_signal)

    return signals

