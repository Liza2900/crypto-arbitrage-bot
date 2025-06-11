import aiohttp
import asyncio

EXCHANGES = ['Bybit', 'MEXC', 'KuCoin', 'BingX', 'Gate']

TRADING_FEES = {
    'KuCoin': 0.001,
    'MEXC': 0.001,
    'Bybit': 0.001,
    'BingX': 0.001,
    'Gate': 0.002
}

WITHDRAWAL_FEES = {
    'USDT': {
        'KuCoin': {'TRC20': 1, 'ERC20': 25},
        'MEXC': {'TRC20': 1},
        'Bybit': {'TRC20': 1},
        'BingX': {'TRC20': 1},
        'Gate': {'TRC20': 1}
    }
    # Інші монети можна додати пізніше
}

SYMBOL_ENDPOINTS = {
    'KuCoin': 'https://api.kucoin.com/api/v1/symbols',
    'MEXC': 'https://api.mexc.com/api/v3/exchangeInfo',
    'Bybit': 'https://api.bybit.com/v5/market/instruments?category=spot',
    'BingX': 'https://open-api.bingx.com/openApi/spot/v1/common/symbols',
    'Gate': 'https://api.gate.io/api/v4/spot/currency_pairs'
}

async def fetch_withdraw_status():
    result = {}
    async with aiohttp.ClientSession() as session:
        # KuCoin
        kucoin_resp = await session.get("https://api.kucoin.com/api/v1/currencies")
        kucoin_data = await kucoin_resp.json()
        result['KuCoin'] = {item['currency']: item['isWithdrawEnabled'] for item in kucoin_data['data']}

        # Bybit
        bybit_resp = await session.get("https://api.bybit.com/v5/asset/coin/query-info")
        bybit_data = await bybit_resp.json()
        result['Bybit'] = {item['name']: any(chain['chainInfo']['chainType'] == 'TRC20' and chain['chainInfo']['canWithdraw'] for chain in item['chains']) for item in bybit_data['result']}

        # Gate
        gate_resp = await session.get("https://api.gate.io/api/v4/wallet/currency_chains")
        gate_data = await gate_resp.json()
        result['Gate'] = {}
        for item in gate_data:
            currency = item['currency']
            withdraw_disabled = item.get('withdraw_disabled', False)
            result['Gate'][currency.upper()] = not withdraw_disabled

        # MEXC і BingX не мають публічного API на це — будемо вважати, що всі монети доступні
        result['MEXC'] = {}
        result['BingX'] = {}

    return result


def select_best_network_for_transfer(coin, from_exchange, to_exchange):
    if coin not in WITHDRAWAL_FEES:
        return None, None

    coin_networks = WITHDRAWAL_FEES[coin]
    if from_exchange not in coin_networks:
        return None, None

    available_networks = coin_networks[from_exchange]
    best_network = min(available_networks.items(), key=lambda x: x[1])
    return best_network  # (мережа, комісія)


def calculate_net_profit(spread_percent, volume_usd, buy_fee, sell_fee, withdraw_fee):
    gross_profit = volume_usd * (spread_percent / 100)
    total_fees = volume_usd * (buy_fee + sell_fee) + withdraw_fee
    return gross_profit - total_fees


def format_arbitrage_message(signal, withdraw_status):
    coin = signal['coin']
    buy_ex = signal['buy_exchange']
    sell_ex = signal['sell_exchange']
    volume = signal['volume']
    spread = signal['spread']
    buy_price = signal['buy_price']
    sell_price = signal['sell_price']

    buy_fee = TRADING_FEES.get(buy_ex, 0)
    sell_fee = TRADING_FEES.get(sell_ex, 0)

    network, withdraw_fee = select_best_network_for_transfer(coin='USDT', from_exchange=buy_ex, to_exchange=sell_ex)
    withdraw_fee = withdraw_fee if withdraw_fee is not None else 0

    withdraw_enabled = withdraw_status.get(buy_ex, {}).get(coin, True)

    net_profit = calculate_net_profit(spread, volume, buy_fee, sell_fee, withdraw_fee)

    message = (
        f"💰 <b>{coin} Арбітраж</b>\n\n"
        f"📉 Купівля: {buy_ex} — <code>{buy_price}$</code>\n"
        f"📈 Продаж: {sell_ex} — <code>{sell_price}$</code>\n"
        f"📊 Обсяг: <code>{volume}$</code>\n"
        f"🔁 Спред до комісій: <code>{spread:.2f}%</code>\n"
        f"💸 Комісії: купівля {buy_fee*100:.2f}%, продаж {sell_fee*100:.2f}%, вивід {withdraw_fee}$\n"
        f"📦 Через мережу: <code>{network or 'невідомо'}</code>\n"
        f"✅ Виведення доступне: {'так' if withdraw_enabled else 'ні'}\n\n"
        f"📈 <b>Чистий прибуток:</b> <code>{net_profit:.2f}$</code>"
    )
    return message


# --- Меню фільтрів ---
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_filters_menu(filters):
    keyboard = [
        [
            InlineKeyboardButton(f"Мін. профіт: {filters['min_profit']}%", callback_data='set_min_profit'),
            InlineKeyboardButton(f"Обсяг: {filters['min_volume']}$", callback_data='set_min_volume')
        ],
        [
            InlineKeyboardButton("Бюджет: ${}".format(filters.get('budget', 100)), callback_data='set_budget')
        ],
        [
            InlineKeyboardButton("Биржі покупки", callback_data='toggle_buy_exchanges'),
            InlineKeyboardButton("Биржі продажу", callback_data='toggle_sell_exchanges')
        ],
        [
            InlineKeyboardButton("🔄 Оновити", callback_data='refresh_signals')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# --- Обробка callback-фільтрів ---
from telegram.ext import CallbackQueryHandler, ContextTypes
from telegram import Update

async def handle_filter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    filters = context.user_data.get('filters', {
        'min_profit': 0.8,
        'min_volume': 10,
        'budget': 100,
        'exchanges_buy': {ex: True for ex in EXCHANGES},
        'exchanges_sell': {ex: True for ex in EXCHANGES}
    })

    if query.data == 'set_min_profit':
        filters['min_profit'] += 0.2
        if filters['min_profit'] > 5:
            filters['min_profit'] = 0.8

    elif query.data == 'set_min_volume':
        filters['min_volume'] += 10
        if filters['min_volume'] > 100:
            filters['min_volume'] = 10

    elif query.data == 'set_budget':
        filters['budget'] *= 2
        if filters['budget'] > 1000:
            filters['budget'] = 50

    elif query.data == 'toggle_buy_exchanges':
        for ex in filters['exchanges_buy']:
            filters['exchanges_buy'][ex] = not filters['exchanges_buy'][ex]

    elif query.data == 'toggle_sell_exchanges':
        for ex in filters['exchanges_sell']:
            filters['exchanges_sell'][ex] = not filters['exchanges_sell'][ex]

    context.user_data['filters'] = filters
    await query.edit_message_reply_markup(reply_markup=build_filters_menu(filters))


# --- Далі: логіка пошуку арбітражу ---
# В наступному кроці буде додано fetch_prices_from_exchanges() та find_arbitrage_opportunities()


