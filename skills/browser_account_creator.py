"""Task preparer skill.

Przygotowuje zlecenie: wykrywa intencję, generuje e-mail i zapisuje task.
"""
import json


def run(query: str = "") -> str:
    if not query:
        return json.dumps({"error": "no query"}, ensure_ascii=False)

    try:
        from skills import intent_detector
        from skills import email_generator
        from skills import task_state_manager
    except Exception as exc:  # pragma: no cover
        return json.dumps({"error": f"helper import failed: {exc}"}, ensure_ascii=False)

    intent_raw = intent_detector.run(query)
    try:
        intent = json.loads(intent_raw)
    except Exception:
        intent = {"intent": "unknown", "platform": "unknown", "confidence": "low"}

    prepared = {"intent": intent}
    if intent.get("intent") == "create_account":
        email_meta = json.loads(email_generator.run(""))
        prepared["email"] = email_meta

    create_command = (
        f"create|{intent.get('intent') or 'unknown'}|{intent.get('platform') or 'unknown'}|"
        f"{json.dumps({'query': query, 'prepared': prepared}, ensure_ascii=False)}"
    )
    task_result = task_state_manager.run(create_command)
    try:
        task_obj = json.loads(task_result)
    except Exception:
        task_obj = {"result": task_result}

    return json.dumps({"task": task_obj, "prepared": prepared}, ensure_ascii=False)
