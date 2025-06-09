DEFAULT_EXCHANGES = ["KuCoin", "MEXC", "OKX", "Bitget", "BingX", "Gate.io", "Bybit"]

# Початкові фільтри для нового користувача
def init_user_filters():
    return {
        "min_profit": 0.5,
        "min_volume": 50,
        "use_futures": False,
        "buy_exchanges": DEFAULT_EXCHANGES.copy(),
        "sell_exchanges": DEFAULT_EXCHANGES.copy(),
        "search_enabled": False
    }

# Обробка натискання на кнопку фільтра
def toggle_filter(user_id, data, filters):
    if data.startswith("filter_profit"):
        filters["min_profit"] = round(filters["min_profit"] + 0.1, 1)
    elif data.startswith("filter_volume"):
        filters["min_volume"] += 10
    elif data.startswith("filter_futures"):
        filters["use_futures"] = not filters["use_futures"]
    elif data.startswith("filter_toggle"):
        filters["search_enabled"] = not filters["search_enabled"]
    elif data.startswith("exchange_buy_"):
        ex = data.replace("exchange_buy_", "")
        if ex in filters["buy_exchanges"]:
            filters["buy_exchanges"].remove(ex)
        else:
            filters["buy_exchanges"].append(ex)
    elif data.startswith("exchange_sell_"):
        ex = data.replace("exchange_sell_", "")
        if ex in filters["sell_exchanges"]:
            filters["sell_exchanges"].remove(ex)
        else:
            filters["sell_exchanges"].append(ex)
    return filters
