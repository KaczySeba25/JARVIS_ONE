"""Intent detector skill.

Analizuje wejście użytkownika i wykrywa intencję, platformę i wymagane dane.
"""
import json

PLATFORMS = ["tiktok", "gmail", "google", "x", "twitter", "facebook", "instagram"]
INTENTS = {
    "create_account": ["otworz konto", "załóż konto", "utwórz konto", "zarejestruj", "create account", "open account"],
    "login": ["zaloguj", "login", "log in"],
    "delete_account": ["usuń konto", "delete account"],
    "research": ["sprawdź", "zbadaj", "research", "wybadaj"],
}


def _detect_platform(text: str) -> str:
    t = text.lower()
    for platform in PLATFORMS:
        if platform in t:
            return platform
    return "unknown"


def _detect_intent(text: str) -> str:
    t = text.lower()
    for intent, patterns in INTENTS.items():
        for pattern in patterns:
            if pattern in t:
                return intent
    if "konto" in t or "account" in t:
        return "create_account"
    return "unknown"


def run(query: str = "") -> str:
    if not query:
        return json.dumps({"intent": "none", "platform": "none", "confidence": "low"}, ensure_ascii=False)
    q = query.lower()
    result = {
        "intent": _detect_intent(q),
        "platform": _detect_platform(q),
        "confidence": "high" if _detect_intent(q) != "unknown" else "low",
    }
    return json.dumps(result, ensure_ascii=False)
