import hmac
import hashlib
import time
import requests
import base64
import json
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

BITGET_API_KEY = os.getenv("BITGET_API_KEY")
BITGET_API_SECRET = os.getenv("BITGET_API_SECRET")
BITGET_API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")
BASE_URL = "https://api.bitget.com"

HEADERS = {
    "Content-Type": "application/json",
    "ACCESS-KEY": BITGET_API_KEY,
    "ACCESS-PASSPHRASE": BITGET_API_PASSPHRASE,
}

def get_timestamp():
    return str(int(time.time() * 1000))

def sign_request(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method.upper()}{request_path}{body}"
    mac = hmac.new(BITGET_API_SECRET.encode(), message.encode(), digestmod=hashlib.sha256)
    return mac.hexdigest()

def get_headers(method, path, body=""):
    timestamp = get_timestamp()
    sign = sign_request(timestamp, method, path, body)
    return {
        **HEADERS,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-SIGN": sign
    }

# === 1. Отримати поточну ціну ===
def get_spot_price(symbol="BTCUSDT"):
    url = f"{BASE_URL}/api/spot/v1/market/ticker?symbol={symbol}"
    try:
        r = requests.get(url)
        return float(r.json()["data"]["close"])
    except:
        return None

# === 2. Список всіх спотових пар ===
def get_all_symbols():
    url = f"{BASE_URL}/api/spot/v1/public/products"
    r = requests.get(url)
    return [item["symbol"] for item in r.json().get("data", [])]

# === 3. Перевірити доступність виводу монети ===
def get_coin_withdrawal_info():
    path = "/api/spot/v1/account/assets"
    url = BASE_URL + path
    headers = get_headers("GET", path)
    r = requests.get(url, headers=headers)
    return r.json()

# === 4. Отримати комісії (можливо потребує окремого endpoint або встановити вручну) ===
DEFAULT_TAKER_FEE = 0.001  # 0.1% стандартно для Bitget

def get_fee():
    return DEFAULT_TAKER_FEE

# === 5. Зразок виклику ===
if __name__ == "__main__":
    print("BTC/USDT:", get_spot_price("BTCUSDT"))
    print("Available pairs:", get_all_symbols()[:5])
    print("Fee:", get_fee())
