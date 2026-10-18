# ================================================================== #
# JARVIS ONE - REMASTERED IMMORTAL ENGINE (ULTIMATE v3.6 - FULL POWER)
# ================================================================== #
import os
import re
import hashlib
import importlib
import sys
import json
import shutil
import traceback
import datetime
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Gwarantujemy dostęp do folderu skills
sys.path.append("skills")

try:
    import semantic_memory as sm
    import vault_manager as vm
except ImportError:
    class Mock:
        def __getattr__(self, name): return lambda *args, **kwargs: "Skill niezaimplementowany"
    sm = Mock()
    vm = Mock()

load_dotenv()

# ================================================================== #
# GLOBALNE KONSTANTY I BEZPIECZEŃSTWO
# ================================================================== #
TOOL_RE = re.compile(r"\[\s*(WRITE_FILE|APPEND_FILE|READ_FILE|LIST_FILES|FETCH_URL|RUN_SKILL|SAVE_SKILL|RECALL|REMEMBER)\s*:")
ACTION_WORDS = ("stworz", "stwórz", "zapisz", "odczytaj", "wczytaj", "sprawdz", "sprawdź", "pobierz", "uruchom", "wykonaj", "dodaj", "zmien", "zmień", "usun", "usuń", "napisz", "wypisz", "wyge", "wygeneruj", "zbuduj", "skasuj", "przenies", "przenieś", "pamietaj", "pamiętaj", "zapamietaj", "zapamiętaj")

MAX_HISTORY_MSGS = 6 
MAX_TOOL_TURNS = 12
MAX_REPEATS = 3 
MAX_REPLY_STORE = 1000

TESTNET_INDICATORS = ("testnet.binance.vision", "testnet.binance.com", "trading_agent_config", "binance_helper")
TRADING_PATTERNS = ("/api/v3/order", "place_order", "place_limit_order", "place_limit_buy", "create_order", "new_order")
PRODUCTION_HOSTS = ("api.binance.com", "api1.binance.com", "api2.binance.com", "api3.binance.com")
PRODUCTION_KEY_NAMES = ("BINANCE_API_KEY", "BINANCE_SECRET_KEY", "BINANCE_SECRET")

ROOT = Path(__file__).resolve().parents[0]
LOG_DIR = ROOT / "data_vault"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LLM_LOG = LOG_DIR / "llm_errors.log"

# ================================================================== #
# ROUTER MODELI (FULL FAILOVER)
# ================================================================== #
client_groq = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
client_nvidia = OpenAI(api_key=os.getenv("NVIDIA_API_KEY"), base_url="https://integrate.api.nvidia.com/v1")

MODELS = {
    "fast": os.getenv("JARVIS_MODEL", "qwen/qwen3.8-27b"), 
    "smart": os.getenv("JARVIS_SMART_MODEL", "openai/gpt-oss-120b"), 
    "fallback": os.getenv("JARVIS_MODEL", "qwen/qwen3.8-27b")
}


def _log_llm_error(name, exc, extra=None):
    try:
        ts = datetime.datetime.utcnow().isoformat()
        with open(LLM_LOG, "a", encoding="utf-8") as fh:
            fh.write(f"\n--- {ts} | {name} ---\n")
            fh.write('EXCEPTION: ' + repr(exc) + "\n")
            fh.write('TRACEBACK:\n')
            fh.write(''.join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
            if extra:
                fh.write('\nEXTRA:\n')
                try:
                    fh.write(str(extra) + "\n")
                except Exception:
                    pass
            fh.write("--- end ---\n")
    except Exception:
        # best-effort logging; do not raise
        pass


def ask_llm_groq(messages):
    try:
        return client_groq.chat.completions.create(model=MODELS["fast"], messages=messages, temperature=0.7, max_tokens=800).choices[0].message.content
    except Exception as e:
        _log_llm_error('GROQ', e)
        raise

def ask_llm_nvidia_smart(messages):
    try:
        return client_nvidia.chat.completions.create(model=MODELS["smart"], messages=messages, temperature=0.7, max_tokens=800).choices[0].message.content
    except Exception as e:
        _log_llm_error('NVIDIA_SMART', e)
        raise

def ask_llm_nvidia_fallback(messages):
    try:
        return client_nvidia.chat.completions.create(model=MODELS["fallback"], messages=messages, temperature=0.7, max_tokens=800).choices[0].message.content
    except Exception as e:
        _log_llm_error('NVIDIA_FALLBACK', e)
        raise

def ask_jarvis(messages):
    # Primary -> GROQ, Smart -> NVIDIA, Fallback -> NVIDIA fallback
    try:
        return ask_llm_groq(messages)
    except Exception:
        print(f"[ROUTER] Groq Fail -> Switching to NVIDIA Smart...", end="\r")
        try:
            return ask_llm_nvidia_smart(messages)
        except Exception:
            try:
                return ask_llm_nvidia_fallback(messages)
            except Exception as e:
                # final fallback: try local web research to provide a helpful reply
                try:
                    from skills import web_research
                    # use last user message as query if available
                    last_msg = ''
                    try:
                        last_msg = messages[-1].get('content','') if messages else ''
                    except Exception:
                        last_msg = ''
                    fallback_query = f"Fallback LLM unavailable. Przekażę zapytanie: {last_msg[:800]}"
                    result = web_research.run(fallback_query)
                    return f"FALLBACK (local web_research):\n{result}"
                except Exception as ex2:
                    _log_llm_error('ALL_MODELS_FAILED', e, extra=ex2)
                    return f"BŁĄD KRYTYCZNY: Wszystkie modele zawiodły i fallback nie powiódł się. Sprawdź {LLM_LOG} dla szczegółów."

# ================================================================== #
# NARZĘDZIA MATEMATYCZNE I TRADINGOWE (WBUDOWANE)
# ================================================================== #
def calculate_margin(balance, position_size, leverage):
    if leverage <= 0: return {"error": "Dźwignia musi być > 0"}
    required_margin = position_size / leverage
    margin_pct = (required_margin / balance * 100) if balance > 0 else 0
    return {"required_margin": round(required_margin, 2), "margin_percentage": round(margin_pct, 2), "is_risky": margin_pct > 50}

class Backtester:
    def __init__(self, initial_capital=10000, leverage=10):
        self.initial_capital = initial_capital
        self.leverage = leverage
        self.current_capital = initial_capital
    def run_backtest(self, price_history):
        if len(price_history) < 2: return {"error": "Za mało danych"}
        pnl_pct = ((price_history[-1] - price_history[0]) / price_history[0]) * self.leverage * 100
        pnl_abs = self.initial_capital * (pnl_pct / 100)
        self.current_capital += pnl_abs
        return {"pnl_pct": round(pnl_pct, 2), "pnl_abs": round(pnl_abs, 2), "final_capital": round(self.current_capital, 2)}

# ================================================================== #
# WALIDACJA I BEZPIECZEŃSTWO
# ================================================================== #
def _validate_skill_write(filepath, content):
    if not filepath.endswith(".py"): return True, ""
    if "skills/" not in filepath and "agents/" not in filepath: return True, ""
    has_testnet = any(sig in content for sig in TESTNET_INDICATORS)
    has_prod = any(h in content for h in PRODUCTION_HOSTS)
    does_trade = any(pat in content for pat in TRADING_PATTERNS)
    if does_trade and not has_testnet: return False, "BŁĄD: Brak testnet."
    if has_prod and does_trade: return False, "BŁĄD: Zakaz produkcji."
    for k in PRODUCTION_KEY_NAMES:
        if k in content: return False, f"BŁĄD: Klucz {k}."
    if not content.lstrip().startswith('"""'): return False, "BŁĄD: Brak docstring."
    if "def run(" not in content: return False, "BŁĄD: Brak run()."
    try: compile(content, filepath, "exec")
    except SyntaxError as e: return False, f"BŁĄD SKŁADNI: {e}"
    return True, ""

# ================================================================== #
# LOGIKA NARZĘDZI
# ================================================================== #
def execute_tool(name, raw):
    raw = raw.strip().rstrip("]")
    if name == "RUN_SKILL":
        if "|" in raw:
            skill_name, arg = [p.strip() for p in raw.split("|", 1)]
        else:
            skill_name, arg = raw, ""
        try:
            module = importlib.import_module(f"skills.{skill_name}")
            importlib.reload(module)
            return f"[WYNIK SKILLA {skill_name if 'skill_name' in locals() else skill_name}]:\n" + module.run(arg)
        except Exception as e: return f"[BŁĄD SKILLA {skill_name}]: {str(e)}"
    
    if name == "WRITE_FILE":
        if "|" not in raw: return "[BŁĄD]: Format sciezka | tresc"
        path, content = [p.strip() for p in raw.split("|", 1)]
        ok, err = _validate_skill_write(path, content)
        if not ok: return f"[ODRZUCONO]: {err}"
        try:
            if os.path.exists(path): shutil.copy2(path, path + ".bak")
            with open(path, "w", encoding="utf-8") as f: f.write(content)
            return f"[WYNIK WRITE_FILE]: Zapisano w {path}"
        except Exception as e: return f"[BŁĄD ZAPISU]: {str(e)}"

    if name == "APPEND_FILE":
        if "|" not in raw: return "[BŁĄD]: Format sciezka | tresc"
        path, content = [p.strip() for p in raw.split("|", 1)]
        try:
            if os.path.exists(path): shutil.copy2(path, path + ".bak")
            with open(path, "a", encoding="utf-8") as f: f.write("\n\n" + content)
            return f"[WYNIK APPEND_FILE]: Dodano do {path}"
        except Exception as e: return f"[BŁD DOPISYWANIA]: {str(e)}"

    if name == "READ_FILE":
        try:
            with open(raw, "r", encoding="utf-8") as f: return f"[WYNIK READ_FILE]:\n{f.read()}"
        except Exception as e: return f"[BŁĄD ODczytu]: {str(e)}"

    if name == "LIST_FILES":
        try:
            path = raw if raw else "."
            files = os.listdir(path)
            return f"[WYNIK LIST_FILES]:\n" + "\n".join(files)
        except Exception as e: return f"[BŁĄD LISTY]: {str(e)}"

    if name == "REMEMBER":
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) < 3: return "[BŁĄD]: Format kategoria|klucz|tresc"
        return f"[WYNIK REMEMBER]:\n{sm.save_memory(parts[0], parts[1], parts[2])}"
    
    if name == "RECALL":
        res = sm.search_memory(raw)
        if not res: return "[WYNIK RECALL]: Brak wyników."
        return f"[WYNIK RECALL]:\n" + "\n".join([f"[{r['category']}] {r['content']}" for r in res])

    return f"[BŁĄD]: Narzędzie {name} nie znane."

def handle_tools(text):
    markers = list(TOOL_RE.finditer(text))
    if not markers: return False, ""
    results = []
    for i, m in enumerate(markers):
        name = m.group(1)
        start = m.end()
        end = markers[i+1].start() if i+1 < len(markers) else len(text)
        arg = text[start:end].strip()
        if name in ("READ_FILE", "LIST_FILES", "RECALL"):
            close_bracket = arg.find("]")
            if close_bracket != -1: arg = arg[:close_bracket].strip()
        results.append(execute_tool(name, arg))
    return True, "\n\n".join(results)

def build_system_prompt():
    recall = ""
    try:
        mems = sm.get_all_memories()
        if mems: recall = "\n".join([f"- {m['content']}" for m in mems[-3:]])
    except: pass
    return f"""Jesteś JARVIS ONE, autonomicznym partnerem Sebastiana.
ZASADY:
1. NARZĘDZIA: Wyłącznie format [NAZWA: argument].
2. INTERNET: Używaj [RUN_SKILL: web_research | "zapytanie"].
3. PROCES: ANALIZA -> PLAN -> WYKONANIE.
4. BEZPIECZEŃSTWO: Trading tylko testnet.binance.vision.
5. UPGRADE: Aby dodać nową funkcję bez usuwania starej, używaj [APPEND_FILE: sciezka | tresc].
6. OCHRONA: Nigdy nie nadpisuj plików krytycznych bez analizy.
7. STYL: Konkretnie, profesjonalnie, po polsku.

ZNACZNIKI:
- [RUN_SKILL: nazwa | arg]
- [WRITE_FILE: sciezka | tresc]
- [APPEND_FILE: sciezka | tresc]
- [READ_FILE: sciezka]
- [LIST_FILES: sciezka]
- [RECALL: zapytanie]
- [REMEMBER: kategoria | klucz | tresc]

KONTEKST:
{recall}
"""

def _fingerprint(text):
    return hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()[:12]

def main():
    print("\n" + "="*60)
    print("   JARVIS ONE - REMASTERED IMMORTAL ENGINE (ULTIMATE v3.6)")
    print("="*60)
    print("Status: SYSTEM ONLINE | Model: " + MODELS["fast"]) 
    print("'exit' aby wyjść.\n")

    history = [{"role": "system", "content": build_system_prompt()}]

    while True:
        try:
            user_input = input("Ty: ").strip()
            if user_input.lower() in ("exit", "quit", "wyjdź"): break
            if not user_input: continue

            history.append({"role": "user", "content": user_input})
            guard_used, last_fp, repeat_count = False, "", 0

            for turn in range(MAX_TOOL_TURNS):
                messages = [history[0]] + history[-MAX_HISTORY_MSGS:]
                print("Jarvis myśli...", end="\r", flush=True)
                reply = ask_jarvis(messages)
                print(f"\nJarvis: {reply}\n")

                fp = _fingerprint(reply)
                if fp == last_fp:
                    repeat_count += 1
                    if repeat_count >= MAX_REPEATS:
                        print("[STOP] Pętla powtórzeń.")
                        break
                else: repeat_count = 0
                last_fp = fp

                executed, result = handle_tools(reply)
                if (not executed and turn == 0 and not guard_used and 
                    any(w in user_input.lower() for w in ACTION_WORDS)):
                    guard_used = True
                    print("[GUARD] Wymuszam użycie narzędzia...\n")
                    history.append({"role": "assistant", "content": reply})
                    history.append({"role": "user", "content": "UWAGA: Użyj formatu [NAZWA: argument]."})
                    continue

                if executed:
                    print(f"[TOOL EXECUTION]\n{result}\n")
                    history.append({"role": "assistant", "content": reply})
                    history.append({"role": "user", "content": f"SYSTEM FEEDBACK:\n{result}"})
                    continue

                history.append({"role": "assistant", "content": reply})
                break
        except KeyboardInterrupt: break
        except Exception as e: 
            # Log unexpected system errors and continue
            try:
                _log_llm_error('SYSTEM', e)
            except Exception:
                pass
            print(f"[SYSTEM ERROR]: {str(e)}")

if __name__ == "__main__":
    main()
