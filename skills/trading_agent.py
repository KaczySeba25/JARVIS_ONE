"""
Trading Agent – BTC/GBP + XAU/GBP na Binance Testnet.
Budżet: 500 GBP. Strategia: DCA limit orders.
Host: testnet.binance.vision
"""

import logging
from datetime import datetime

from agents.trading_binance.helper import (
    get_balance,
    get_ticker,
    place_limit_order,
)
from agents.trading_binance.config import PAIRS, BUDGET_GBP, MAX_ORDER_GBP

logger = logging.getLogger("trading_agent")


def _calc_limit_price(ticker: dict, side: str, offset_pct: float = 0.5) -> float:
    bid = float(ticker["bidPrice"])
    ask = float(ticker["askPrice"])
    if side == "BUY":
        price = ask * (1 - offset_pct / 100)
    else:
        price = bid * (1 + offset_pct / 100)
    return round(price, 2)


def _dca_split(budget: float, n_pairs: int) -> float:
    return round(budget / n_pairs, 2)


def run(cycles: int = 1):
    logger.info("=== TRADING AGENT START ===")
    logger.info(f"Budget: {BUDGET_GBP} GBP | Pairs: {PAIRS}")
    results = []

    for cycle in range(cycles):
        ts = datetime.utcnow().isoformat()
        logger.info(f"--- Cycle {cycle + 1} @ {ts} ---")

        balance_gbp = get_balance("GBP")
        logger.info(f"Balance GBP: {balance_gbp}")

        per_pair = _dca_split(balance_gbp, len(PAIRS))
        per_pair = min(per_pair, MAX_ORDER_GBP)

        for pair in PAIRS:
            try:
                ticker = get_ticker(pair)
                price = _calc_limit_price(ticker, "BUY")
                qty = round(per_pair / price, 6)
                order = place_limit_order(
                    symbol=pair,
                    side="BUY",
                    quantity=qty,
                    price=price,
                )
                logger.info(f"Order placed: {pair} BUY {qty} @ {price}")
                results.append({
                    "pair": pair,
                    "side": "BUY",
                    "qty": qty,
                    "price": price,
                    "orderId": order.get("orderId"),
                    "status": order.get("status"),
                })
            except Exception as e:
                logger.error(f"Error on {pair}: {e}")
                results.append({"pair": pair, "error": str(e)})

    logger.info("=== TRADING AGENT DONE ===")
    return {"cycles": cycles, "orders": results}