"""Auto-Rollback Manager Gadget.

Tworzy snapshoty plików krytycznych przed modyfikacją i umożliwia przywracanie z backupów.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / "data_vault" / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = ROOT / "data_vault" / "rollback_index.json"


def _read_index():
    if INDEX_FILE.exists():
        try:
            return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _write_index(data):
    INDEX_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def run(arg: str = "") -> str:
    if not arg:
        return json.dumps({"error": "empty command"}, ensure_ascii=False)
    parts = [p.strip() for p in arg.split("|")]
    cmd = parts[0].lower()
    if cmd == "snapshot":
        if len(parts) < 2:
            return json.dumps({"error": "usage: snapshot|path"}, ensure_ascii=False)
        src = Path(parts[1])
        if not src.exists():
            return json.dumps({"error": f"path not found: {src}"}, ensure_ascii=False)
        backup_name = f"{src.name}_{abs(hash(str(src)))}.bak"
        dest = BACKUP_DIR / backup_name
        shutil.copy2(src, dest)
        idx = _read_index()
        idx[backup_name] = {"source": str(src), "backup_path": str(dest)}
        _write_index(idx)
        return json.dumps({"backup": backup_name, "source": str(src), "dest": str(dest)}, ensure_ascii=False)
    if cmd == "list":
        return json.dumps(_read_index(), ensure_ascii=False)
    if cmd == "restore":
        if len(parts) < 2:
            return json.dumps({"error": "usage: restore|backup_name"}, ensure_ascii=False)
        idx = _read_index()
        item = idx.get(parts[1])
        if not item:
            return json.dumps({"error": "backup not found"}, ensure_ascii=False)
        src = Path(item["backup_path"])
        dst = Path(item["source"])
        if src.exists():
            shutil.copy2(src, dst)
            return json.dumps({"restored": str(dst), "from": str(src)}, ensure_ascii=False)
        return json.dumps({"error": "backup missing"}, ensure_ascii=False)
    return json.dumps({"error": "unknown command"}, ensure_ascii=False)
