"""
Config modułu tradingowego Binance Testnet.
Wszystkie operacje kierowane wyłącznie do testnet.binance.vision.
"""

from vault_manager import vault

# --- HOST (wyszukiwany przez walidator) ---
BASE_URL = "https://testnet.binance.vision"

# --- KLUCZE Z VAULTA ---
API_KEY = vault.get_secret("BINANCE_TESTNET_API_KEY")
API_SECRET = vault.get_secret("BINANCE_TESTNET_SECRET")

# --- PARAMETRY PORTFELA ---
BUDGET_GBP = 500.0
PAIRS = ["BTCGBP", "XAUGBP"]
ORDER_TYPE = "LIMIT"
MAX_ORDER_GBP = 50.0

# --- INTERWAŁY ---
POLL_INTERVAL_SEC = 60
RETRY_LIMIT = 3


def run():
    return {
        "status": "config_loaded",
        "base_url": BASE_URL,
        "pairs": PAIRS,
        "budget_gbp": BUDGET_GBP,
        "api_key_set": bool(API_KEY),
        "api_secret_set": bool(API_SECRET),
    }