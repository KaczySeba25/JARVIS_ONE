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
