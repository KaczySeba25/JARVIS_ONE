"""
Helper Binance Testnet – signing HMAC i requesty API.
Host: testnet.binance.vision
"""

import time
import hmac
import hashlib
import urllib.parse
import requests

from .config import BASE_URL, API_KEY, API_SECRET


def _sign(params: dict) -> str:
    query = urllib.parse.urlencode(params)
    return hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()


def request_signed(method: str, path: str, params: dict = None, retries: int = 3) -> dict:
    params = params or {}
    params["timestamp"] = int(time.time() * 1000)
    params["recvWindow"] = 5000
    query = urllib.parse.urlencode(params)
    signature = _sign(params)
    full_path = f"{path}?{query}&signature={signature}"
    url = BASE_URL + full_path
    headers = {
        "X-MBX-APIKEY": API_KEY,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    last_err = None
    for _ in range(retries):
        try:
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=10)
            else:
                r = requests.post(url, headers=headers, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(2)
    raise last_err


def get_balance(quote_asset: str = "GBP") -> float:
    data = request_signed("GET", "/api/v3/account")
    for b in data.get("balances", []):
        if b["asset"] == quote_asset:
            return float(b["free"])
    return 0.0


def get_ticker(symbol: str) -> dict:
    url = f"{BASE_URL}/api/v3/ticker/bookTicker?symbol={symbol}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def place_limit_order(symbol: str, side: str, price: float, quantity: float) -> dict:
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "timeInForce": "GTC",
        "price": f"{price:.2f}",
        "quantity": f"{quantity:.8f}",
    }
    return request_signed("POST", "/api/v3/order", params)


def cancel_order(symbol: str, order_id: int) -> dict:
    params = {"symbol": symbol, "orderId": order_id}
    return request_signed("DELETE", "/api/v3/order", params)


def run():
    return {"status": "helper_ready", "base_url": BASE_URL}