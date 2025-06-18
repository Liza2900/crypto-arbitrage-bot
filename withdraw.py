from kucoin_withdraw import get_kucoin_withdraw_info
from mexc_withdraw import get_mexc_withdraw_info
from okx_withdraw import get_okx_withdraw_info
from gateio_withdraw import get_gateio_withdraw_info
from bingx_withdraw import get_bingx_withdraw_info
from bitget_withdraw import get_bitget_withdraw_info
from coinex_withdraw import get_coinex_withdraw_info

def get_withdraw_info(exchange_name: str, symbol: str) -> dict:
    """
    Return withdraw info for a specific exchange and symbol.
    Example return:
    {
        "networks": ["TRC20", "ERC20"],
        "fees": {"TRC20": 1.0, "ERC20": 5.0},
        "can_withdraw": True,
        "estimated_time": "~10 min"
    }
    """
    try:
        exchange_name = exchange_name.lower()
        if exchange_name == "kucoin":
            return get_kucoin_withdraw_info(symbol)
        elif exchange_name == "mexc":
            return get_mexc_withdraw_info(symbol)
        elif exchange_name == "okx":
            return get_okx_withdraw_info(symbol)
        elif exchange_name == "gate.io" or exchange_name == "gateio":
            return get_gateio_withdraw_info(symbol)
        elif exchange_name == "bingx":
            return get_bingx_withdraw_info(symbol)
        elif exchange_name == "bitget":
            return get_bitget_withdraw_info(symbol)
        elif exchange_name == "coinex":
            return get_coinex_withdraw_info(symbol)
        else:
            return {
                "networks": [],
                "fees": {},
                "can_withdraw": False,
                "estimated_time": None
            }
    except Exception as e:
        print(f"Withdraw info error for {exchange_name}/{symbol}: {e}")
        return {
            "networks": [],
            "fees": {},
            "can_withdraw": False,
            "estimated_time": None
        }
