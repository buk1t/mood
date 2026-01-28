import json
import os
from datetime import datetime
from pathlib import Path

import webview

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
WEB_DIR = APP_DIR / "web"
ENTRIES_PATH = DATA_DIR / "entries.json"


def now_iso():
    # Local time ISO; good enough for personal journaling
    return datetime.now().astimezone().isoformat(timespec="seconds")


def ensure_storage():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ENTRIES_PATH.exists():
        ENTRIES_PATH.write_text("[]", encoding="utf-8")


def load_entries():
    ensure_storage()
    try:
        return json.loads(ENTRIES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # If file gets corrupted, preserve it and start fresh
        backup = ENTRIES_PATH.with_suffix(".corrupt.json")
        ENTRIES_PATH.replace(backup)
        ENTRIES_PATH.write_text("[]", encoding="utf-8")
        return []


def save_entries(entries):
    ensure_storage()
    ENTRIES_PATH.write_text(json.dumps(
        entries, indent=2, ensure_ascii=False), encoding="utf-8")


class API:
    def ping(self):
        return {"ok": True}

    def list_entries(self):
        entries = load_entries()
        # newest first
        entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
        return entries

    def add_entry(self, entry):
        entries = load_entries()

        ts = now_iso()
        entry = dict(entry or {})
        entry.setdefault("timestamp", ts)
        entry.setdefault("date", ts[:10])
        entry.setdefault("id", entry["timestamp"])

        entries.append(entry)
        save_entries(entries)
        return {"ok": True, "id": entry["id"]}


if __name__ == "__main__":
    ensure_storage()
    api = API()

    window = webview.create_window(
        title="Mood Journal",
        url=str(WEB_DIR / "index.html"),
        js_api=api,
        width=920,
        height=720,
        resizable=True,
        frameless=False
    )
    webview.start(private_mode=False)
