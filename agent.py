#!/usr/bin/env python3
# Header bootstrap in agent.py: ensure dependencies and AUTO_APPROVE behavior
import os
import re
import hashlib
import importlib
import sys
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS_DIR = ROOT / "skills"


def _module_name_from_requirement(requirement: str) -> str:
    req = requirement.strip()
    if not req or req.startswith("#"):
        return ""
    req = req.split(";", 1)[0].strip()
    req = req.split("[", 1)[0]
    for sep in ("==", ">=", "<=", "~=", "!=", ">", "<"):
        if sep in req:
            req = req.split(sep, 1)[0]
            break
    return req.strip()


def ensure_python_dependencies():
    """Instaluje brakujące biblioteki bez pytania o zgodę jeśli są wymagane do działania agenta."""
    req_file = ROOT / "requirements.txt"
    if not req_file.exists():
        return

    mapping = {
        "beautifulsoup4": "bs4",
        "duckduckgo-search": "duckduckgo_search",
        "python-dotenv": "dotenv",
        "tavily-python": "tavily",
        "cryptography": "cryptography",
        "playwright": "playwright",
    }

    packages = []
    for raw in req_file.read_text(encoding="utf-8").splitlines():
        item = raw.strip()
        if not item or item.startswith("#"):
            continue
        packages.append(item)

    missing = []
    for pkg in packages:
        module_name = mapping.get(_module_name_from_requirement(pkg), _module_name_from_requirement(pkg))
        if not module_name:
            continue
        try:
            __import__(module_name)
        except Exception:
            missing.append(pkg)

    if missing:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            *missing,
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SKILLS_DIR))
ensure_python_dependencies()

from openai import OpenAI
from dotenv import load_dotenv

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

# Read autonomy flags from env
AUTO_APPROVE = os.getenv("AUTO_APPROVE", "true").lower() == "true"
AUTO_RUN_BROWSER = os.getenv("AUTO_RUN_BROWSER", "true").lower() == "true"

# ================================================================== #
# GLOBALNE KONSTANTY I BEZPIECZEŃSTWO
# ================================================================== #
TOOL_RE = re.compile(r"\[\s*(WRITE_FILE|APPEND_FILE|READ_FILE|LIST_FILES|FETCH_URL|RUN_SKILL|SAVE_SKILL|RECALL|REMEMBER)\s*:")
ACTION_WORDS = ("stworz", "stwórz", "zapisz", "odczytaj", "wczytaj", "sprawdz", "sprawdź", "pobierz", "uruchom", "wykonaj", "dodaj", "zmien", "zmień", "usun", "usuń", "napisz", "wypisz")

MAX_HISTORY_MSGS = 6 
MAX_TOOL_TURNS = 12
MAX_REPEATS = 3 
MAX_REPLY_STORE = 1000

TESTNET_INDICATORS = ("testnet.binance.vision", "testnet.binance.com", "trading_agent_config", "binance_helper")
TRADING_PATTERNS = ("/api/v3/order", "place_order", "place_limit_order", "place_limit_buy", "create_order", "new_order")
PRODUCTION_HOSTS = ("api.binance.com", "api1.binance.com", "api2.binance.com", "api3.binance.com")
PRODUCTION_KEY_NAMES = ("BINANCE_API_KEY", "BINANCE_SECRET_KEY", "BINANCE_SECRET")

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

def ask_llm_groq(messages):
    return client_groq.chat.completions.create(model=MODELS["fast"], messages=messages, temperature=0.7, max_tokens=800).choices[0].message.content

def ask_llm_nvidia_smart(messages):
    return client_nvidia.chat.completions.create(model=MODELS["smart"], messages=messages, temperature=0.7, max_tokens=800).choices[0].message.content

def ask_llm_nvidia_fallback(messages):
    return client_nvidia.chat.completions.create(model=MODELS["fallback"], messages=messages, temperature=0.7, max_tokens=800).choices[0].message.content

def ask_jarvis(messages):
    try:
        return ask_llm_groq(messages)
    except Exception as e:
        print(f"[ROUTER] Groq Fail -> Switching to NVIDIA Smart...", end="\r")
        try:
            return ask_llm_nvidia_smart(messages)
        except Exception as e:
            try:
                return ask_llm_nvidia_fallback(messages)
            except Exception as e:
                return f"BŁĄD KRYTYCZNY: Wszystkie modele zawiodły. {e}"

# rest of file continues unchanged (the rest of the code is already in repository)
