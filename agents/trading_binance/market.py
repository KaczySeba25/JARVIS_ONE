"""
market.py - Modul danych rynkowych dla agenta tradingowego.
Zrodlo: Binance public REST API (bez kluczy, bez autoryzacji).
Obsluguje: BTC/GBP, PAXG/USDT (zloto jako token PAXG = 1 uncja trojanska).
"""
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
CACHE_DIR = HERE / "cache"
CACHE_DIR.mkdir(exist_ok=True)

BINANCE_BASE = "https://api.binance.com"
REQUEST_TIMEOUT = 15
MIN_DELAY_BETWEEN_REQUESTS = 0.5   # sekundy - chroni przed rate limitem

_last_request_time = 0.0


# ------------------------------------------------------------------ #
#  NISKOPOZIOMOWE HTTP
# ------------------------------------------------------------------ #

def _http_get_json(url, params=None):
    """Pobiera JSON z Binance z opoznieniem i timeoutem."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < MIN_DELAY_BETWEEN_REQUESTS:
        time.sleep(MIN_DELAY_BETWEEN_REQUESTS - elapsed)

    if params:
        qs = "&".join(str(k) + "=" + str(v) for k, v in params.items())
        full = url + "?" + qs
    else:
        full = url

    req = urllib.request.Request(full, headers={"User-Agent": "JARVIS-ONE/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        _last_request_time = time.time()
        return data
    except urllib.error.HTTPError as e:
        _last_request_time = time.time()
        raise RuntimeError("HTTP " + str(e.code) + " dla " + full)
    except Exception as e:
        _last_request_time = time.time()
        raise RuntimeError("Blad sieci: " + str(e))


# ------------------------------------------------------------------ #
#  CENY BIEZACE
# ------------------------------------------------------------------ #

def get_price(symbol):
    """
    Zwraca aktualna cene dla symbolu (np. 'BTCGBP', 'PAXGUSDT').
    Zwraca float lub None.
    """
    try:
        data = _http_get_json(
            BINANCE_BASE + "/api/v3/ticker/price",
            {"symbol": symbol.upper()}
        )
        return float(data["price"])
    except Exception as e:
        print("[market] blad get_price(" + symbol + "): " + str(e))
        return None


def get_24h_stats(symbol):
    """Zwraca dict z 24h statystykami: price, change%, high, low, volume."""
    try:
        data = _http_get_json(
            BINANCE_BASE + "/api/v3/ticker/24hr",
            {"symbol": symbol.upper()}
        )
        return {
            "symbol": data["symbol"],
            "price": float(data["lastPrice"]),
            "change_pct": float(data["priceChangePercent"]),
            "high": float(data["highPrice"]),
            "low": float(data["lowPrice"]),
            "volume": float(data["volume"]),
            "quote_volume": float(data["quoteVolume"]),
        }
    except Exception as e:
        print("[market] blad get_24h_stats(" + symbol + "): " + str(e))
        return None


# ------------------------------------------------------------------ #
#  SWIECE HISTORYCZNE (KLINES)
# ------------------------------------------------------------------ #

def get_klines(symbol, interval="1h", limit=500, start_time_ms=None, end_time_ms=None):
    """
    Pobiera swiece z Binance.
    interval: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1mo
    limit: max 1000 na zapytanie
    Zwraca liste dictow: {open_time, open, high, low, close, volume, close_time}
    """
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": min(int(limit), 1000),
    }
    if start_time_ms is not None:
        params["startTime"] = int(start_time_ms)
    if end_time_ms is not None:
        params["endTime"] = int(end_time_ms)

    try:
        raw = _http_get_json(BINANCE_BASE + "/api/v3/klines", params)
    except Exception as e:
        print("[market] blad get_klines: " + str(e))
        return []

    out = []
    for k in raw:
        out.append({
            "open_time": int(k[0]),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
            "close_time": int(k[6]),
        })
    return out


def get_history(symbol, interval="1h", days=365):
    """
    Pobiera historie przez paginacje (limit 1000 na zapytanie).
    days=365 => rok wstecz.
    Zwraca liste swiec posortowana rosnaco po czasie.
    """
    interval_ms = _interval_to_ms(interval)
    if interval_ms is None:
        print("[market] nieznany interval: " + interval)
        return []

    now_ms = int(time.time() * 1000)
    start_ms = now_ms - (days * 24 * 60 * 60 * 1000)

    all_klines = []
    cursor = start_ms
    safety = 0

    while cursor < now_ms and safety < 50:  # max 50 zapytan
        safety += 1
        batch = get_klines(symbol, interval=interval, limit=1000,
                           start_time_ms=cursor, end_time_ms=now_ms)
        if not batch:
            break
        all_klines.extend(batch)
        last_close_time = batch[-1]["close_time"]
        if last_close_time <= cursor:
            break
        cursor = last_close_time + 1
        print("[market] pobrano " + str(len(all_klines)) + " swiec...")

    # deduplikacja po open_time
    seen = set()
    unique = []
    for k in all_klines:
        if k["open_time"] in seen:
            continue
        seen.add(k["open_time"])
        unique.append(k)
    unique.sort(key=lambda x: x["open_time"])
    return unique


def _interval_to_ms(interval):
    """Zwraca dlugosc interwalu w milisekundach."""
    table = {
        "1m": 60_000,
        "5m": 300_000,
        "15m": 900_000,
        "30m": 1_800_000,
        "1h": 3_600_000,
        "2h": 7_200_000,
        "4h": 14_400_000,
        "6h": 21_600_000,
        "8h": 28_800_000,
        "12h": 43_200_000,
        "1d": 86_400_000,
        "3d": 259_200_000,
        "1w": 604_800_000,
    }
    return table.get(interval)


# ------------------------------------------------------------------ #
#  CACHE LOKALNY
# ------------------------------------------------------------------ #

def save_cache(symbol, interval, klines):
    """Zapisuje swiece do cache (JSON)."""
    fname = CACHE_DIR / (symbol.upper() + "_" + interval + ".json")
    payload = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol.upper(),
        "interval": interval,
        "count": len(klines),
        "klines": klines,
    }
    fname.write_text(json.dumps(payload), encoding="utf-8")
    return str(fname)


def load_cache(symbol, interval, max_age_hours=24):
    """Wczytuje cache jesli istnieje i nie jest za stary."""
    fname = CACHE_DIR / (symbol.upper() + "_" + interval + ".json")
    if not fname.exists():
        return None
    try:
        payload = json.loads(fname.read_text(encoding="utf-8"))
        saved_at = datetime.fromisoformat(payload["saved_at"])
        age_h = (datetime.now(timezone.utc) - saved_at).total_seconds() / 3600
        if age_h > max_age_hours:
            return None
        return payload["klines"]
    except Exception:
        return None


def get_klines_cached(symbol, interval, days=30, force_refresh=False):
    """Pobiera swiece z cache albo z Binance."""
    if not force_refresh:
        cached = load_cache(symbol, interval)
        if cached:
            print("[market] cache hit: " + symbol + " " + interval
                  + " (" + str(len(cached)) + " swiec)")
            return cached
    print("[market] pobieram z Binance: " + symbol + " " + interval
          + " (" + str(days) + " dni)")
    klines = get_history(symbol, interval=interval, days=days)
    if klines:
        save_cache(symbol, interval, klines)
    return klines


# ------------------------------------------------------------------ #
#  WSKAZNIKI TECHNICZNE (czysty Python, bez zaleznosci)
# ------------------------------------------------------------------ #

def ema(values, period):
    """
    Exponential Moving Average.
    Zwraca liste tej samej dlugosci co values (pierwsze period-1 to None).
    """
    if len(values) < period:
        return [None] * len(values)
    k = 2.0 / (period + 1)
    out = [None] * (period - 1)
    sma = sum(values[:period]) / period
    out.append(sma)
    prev = sma
    for v in values[period:]:
        prev = v * k + prev * (1 - k)
        out.append(prev)
    return out


def rsi(closes, period=14):
    """
    Relative Strength Index.
    Zwraca liste tej samej dlugosci co closes (pierwsze period to None).
    """
    n = len(closes)
    if n <= period:
        return [None] * n

    out = [None] * period
    gains = []
    losses = []
    for i in range(1, period + 1):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        out.append(100.0)
    else:
        rs = avg_gain / avg_loss
        out.append(100.0 - (100.0 / (1.0 + rs)))

    for i in range(period + 1, n):
        diff = closes[i] - closes[i - 1]
        gain = max(diff, 0)
        loss = max(-diff, 0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        if avg_loss == 0:
            out.append(100.0)
        else:
            rs = avg_gain / avg_loss
            out.append(100.0 - (100.0 / (1.0 + rs)))

    return out


def macd(closes, fast=12, slow=26, signal=9):
    """
    MACD.
    Zwraca dict: {macd, signal, histogram} - kazda lista dlugosci len(closes).
    """
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)

    macd_line = []
    for f, s in zip(ema_fast, ema_slow):
        if f is None or s is None:
            macd_line.append(None)
        else:
            macd_line.append(f - s)

    macd_clean = [x for x in macd_line if x is not None]
    if len(macd_clean) < signal:
        return {"macd": macd_line, "signal": [None] * len(closes),
                "histogram": [None] * len(closes)}

    sig_clean = ema(macd_clean, signal)
    signal_line = [None] * (len(closes) - len(sig_clean)) + sig_clean

    histogram = []
    for m, s in zip(macd_line, signal_line):
        if m is None or s is None:
            histogram.append(None)
        else:
            histogram.append(m - s)

    return {"macd": macd_line, "signal": signal_line, "histogram": histogram}


def sma(values, period):
    """Simple Moving Average."""
    if len(values) < period:
        return [None] * len(values)
    out = [None] * (period - 1)
    window_sum = sum(values[:period])
    out.append(window_sum / period)
    for i in range(period, len(values)):
        window_sum += values[i] - values[i - period]
        out.append(window_sum / period)
    return out


# ------------------------------------------------------------------ #
#  TEST
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    print("=== TEST MARKET.PY ===\n")

    for sym in ("BTCGBP", "PAXGUSDT"):
        print("--- " + sym + " ---")
        p = get_price(sym)
        print("cena: " + str(p))

        st = get_24h_stats(sym)
        if st:
            print("24h: " + str(st["change_pct"]) + "% | high "
                  + str(st["high"]) + " | low " + str(st["low"]))

        kl = get_klines(sym, interval="1h", limit=100)
        if kl:
            closes = [k["close"] for k in kl]
            print("swiec: " + str(len(kl)))
            print("ostatnie close: " + str(closes[-1]))
            r = rsi(closes, 14)
            print("RSI(14): " + str(round(r[-1], 2) if r[-1] is not None else "?"))
            m = macd(closes)
            print("MACD: " + str(round(m["macd"][-1], 4)
                                  if m["macd"][-1] is not None else "?"))
            print("MACD hist: " + str(round(m["histogram"][-1], 4)
                                      if m["histogram"][-1] is not None else "?"))
        print()