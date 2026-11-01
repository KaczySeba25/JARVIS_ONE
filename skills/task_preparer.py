"""Task state manager.

Zarządza kolejką zadań w data_vault/tasks.json.
"""
import json
import uuid
from pathlib import Path

DATA_VAULT = Path("data_vault")
DATA_VAULT.mkdir(exist_ok=True)
TASKS_FILE = DATA_VAULT / "tasks.json"


def _read():
    if not TASKS_FILE.exists():
        return []
    try:
        return json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write(items):
    TASKS_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def run(arg: str = "") -> str:
    if not arg:
        return json.dumps({"error": "empty command"}, ensure_ascii=False)
    parts = [p.strip() for p in arg.split("|")]
    cmd = parts[0].lower()

    if cmd == "create":
        if len(parts) < 4:
            return json.dumps({"error": "usage: create|type|platform|metadata_json"}, ensure_ascii=False)
        tasks = _read()
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "type": parts[1],
            "platform": parts[2],
            "metadata": json.loads(parts[3]) if parts[3].startswith("{") else {"raw": parts[3]},
            "status": "prepared",
        }
        tasks.append(task)
        _write(tasks)
        return json.dumps(task, ensure_ascii=False)

    if cmd == "list":
        return json.dumps(_read(), ensure_ascii=False)

    if cmd == "get":
        if len(parts) < 2:
            return json.dumps({"error": "usage: get|task_id"}, ensure_ascii=False)
        for task in _read():
            if task.get("id") == parts[1]:
                return json.dumps(task, ensure_ascii=False)
        return json.dumps({}, ensure_ascii=False)

    if cmd == "update":
        if len(parts) < 3:
            return json.dumps({"error": "usage: update|task_id|metadata_json"}, ensure_ascii=False)
        tasks = _read()
        for idx, task in enumerate(tasks):
            if task.get("id") == parts[1]:
                payload = json.loads(parts[2]) if parts[2].startswith("{") else {"raw": parts[2]}
                tasks[idx]["metadata"].update(payload)
                _write(tasks)
                return json.dumps(tasks[idx], ensure_ascii=False)
        return json.dumps({"error": "task not found"}, ensure_ascii=False)

    return json.dumps({"error": "unknown command"}, ensure_ascii=False)
