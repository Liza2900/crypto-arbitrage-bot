from kucoin_withdraw import get_kucoin_withdraw_info
from mexc_withdraw import get_mexc_withdraw_info
from okx_withdraw import get_okx_withdraw_info
from bingx_withdraw import get_bingx_withdraw_info
from bitget_withdraw import get_bitget_withdraw_info
from gateio_withdraw import get_withdraw_info as get_gateio_withdraw_info
from coinex_withdraw import get_coinex_withdraw_info

# Централізований виклик функцій для кожної біржі
async def get_withdraw_info(currency: str) -> dict:
    withdraw_info = {}

    withdraw_info["KuCoin"] = await get_kucoin_withdraw_info(currency)
    withdraw_info["MEXC"] = await get_mexc_withdraw_info(currency)
    withdraw_info["OKX"] = await get_okx_withdraw_info(currency)
    withdraw_info["BingX"] = await get_bingx_withdraw_info(currency)
    withdraw_info["Bitget"] = await get_bitget_withdraw_info(currency)
    withdraw_info["Gate.io"] = await get_gateio_withdraw_info(currency)
    withdraw_info["CoinEx"] = await get_coinex_withdraw_info(currency)

    return withdraw_info
