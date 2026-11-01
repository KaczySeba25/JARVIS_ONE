"""Self-repair utilities: detect missing packages and optionally install them.

This module is conservative: it will only suggest installs and will perform them
only after explicit human confirmation via utils.human_prompt.ask_human.
"""
import importlib
import subprocess
from utils.human_prompt import ask_human


def ensure_packages(pkgs):
    missing = []
    for p in pkgs:
        try:
            importlib.import_module(p)
        except Exception:
            missing.append(p)
    if not missing:
        return True, []
    msg = f"Brakuje pakietow: {missing}. Czy zainstalowac? (tak/nie)"
    resp = ask_human(msg)
    if resp.strip().lower() in ('tak','t','y','yes'):
        for p in missing:
            try:
                subprocess.check_call(["pip", "install", p])
            except Exception as e:
                return False, [str(e)]
        return True, []
    return False, missing
