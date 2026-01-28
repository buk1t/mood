# mood_app/api.py
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from .storage import Paths, load_entries, now_iso, save_entries
from .updater import check_for_updates_and_apply


class API:
    def __init__(self, app_name: str, paths: Paths):
        self.app_name = app_name
        self.paths = paths

    def ping(self):
        return {"ok": True}

    def list_entries(self):
        entries = load_entries(self.paths)
        entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
        return entries

    def add_entry(self, entry: dict[str, Any] | None):
        entries = load_entries(self.paths)

        ts = now_iso()
        e = dict(entry or {})
        e.setdefault("timestamp", ts)
        e.setdefault("date", ts[:10])
        e.setdefault("id", e["timestamp"])

        entries.append(e)
        save_entries(self.paths, entries)
        return {"ok": True, "id": e["id"]}

    def get_installed_version(self):
        if self.paths.installed_version_path.exists():
            return self.paths.installed_version_path.read_text(encoding="utf-8")
        return None

    def check_for_updates(self):
        """
        Called from the UI.
        Returns a dict with status and (optionally) restart_required.
        """
        result = check_for_updates_and_apply(
            repo_owner="buk1t",
            repo_name="mood",
            paths=self.paths,
        )
        return result

    def restart_app(self):
        """
        Relaunch current executable and exit.
        Works for dev + packaged builds (generally).
        """
        python = sys.executable
        argv = [python] + sys.argv

        # On mac app bundles, sys.executable is inside the bundle; argv should still work.
        os.execv(python, argv)
