import httpx

async def get_prices():
    url = "https://api.mexc.com/api/v3/ticker/bookTicker"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

    result = {}
    for item in data:
        symbol = item['symbol']
        if symbol.endswith("USDT") and not symbol.endswith("3LUSDT") and not symbol.endswith("3SUSDT"):
            price = float(item['askPrice'])
            coin = symbol.replace("USDT", "")
            result[coin] = {
                "price": price,
                "volume": 100,  # або реальний обсяг
                "withdraw_fee": 1,  # або дійсна комісія
                "network": "TRC20",
                "transfer_time": "≈5 хв"
            }

    return result
