from kucoin_withdraw import get_kucoin_withdraw_info
from mexc_withdraw import get_mexc_withdraw_info
from okx_withdraw import get_okx_withdraw_info
from bingx_withdraw import get_bingx_withdraw_info
from bitget_withdraw import get_bitget_withdraw_info
from gateio_withdraw import get_withdraw_info as get_gateio_withdraw_info
from coinex_withdraw import get_coinex_withdraw_info
import logging

async def get_withdraw_info(currency: str) -> dict:
    withdraw_info = {}

    try:
        withdraw_info["KuCoin"] = await get_kucoin_withdraw_info(currency)
    except Exception as e:
        logging.warning(f"Withdraw info error for KuCoin/{currency}: {e}")
        withdraw_info["KuCoin"] = {}

    try:
        withdraw_info["MEXC"] = await get_mexc_withdraw_info(currency)
    except Exception as e:
        logging.warning(f"Withdraw info error for MEXC/{currency}: {e}")
        withdraw_info["MEXC"] = {}

    try:
        withdraw_info["OKX"] = await get_okx_withdraw_info(currency)
    except Exception as e:
        logging.warning(f"Withdraw info error for OKX/{currency}: {e}")
        withdraw_info["OKX"] = {}

    try:
        withdraw_info["BingX"] = await get_bingx_withdraw_info(currency)
    except Exception as e:
        logging.warning(f"Withdraw info error for BingX/{currency}: {e}")
        withdraw_info["BingX"] = {}

    try:
        withdraw_info["Bitget"] = await get_bitget_withdraw_info(currency)
    except Exception as e:
        logging.warning(f"Withdraw info error for Bitget/{currency}: {e}")
        withdraw_info["Bitget"] = {}

    try:
        withdraw_info["Gate.io"] = await get_gateio_withdraw_info(currency)
    except Exception as e:
        logging.warning(f"Withdraw info error for Gate.io/{currency}: {e}")
        withdraw_info["Gate.io"] = {}

    try:
        withdraw_info["CoinEx"] = await get_coinex_withdraw_info(currency)
    except Exception as e:
        logging.warning(f"Withdraw info error for CoinEx/{currency}: {e}")
        withdraw_info["CoinEx"] = {}

    return withdraw_info
