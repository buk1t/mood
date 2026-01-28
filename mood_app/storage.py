# mood_app/storage.py
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Paths:
    support_dir: Path
    data_dir: Path
    entries_path: Path
    meta_path: Path
    installed_version_path: Path
    web_dir: Path
    app_dir: Path


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def resolve_paths(app_name: str, support_dir: Path | None = None) -> Paths:
    if support_dir is None:
        support_dir = Path.home() / "Library" / "Application Support" / app_name

    data_dir = support_dir / "data"
    app_dir = support_dir / "app"
    web_dir = support_dir / "web"

    return Paths(
        support_dir=support_dir,
        data_dir=data_dir,
        entries_path=data_dir / "entries.json",
        meta_path=data_dir / "meta.json",
        installed_version_path=support_dir / "installed_version.json",
        web_dir=web_dir,
        app_dir=app_dir,
    )


def ensure_storage(paths: Paths) -> None:
    paths.support_dir.mkdir(parents=True, exist_ok=True)
    paths.data_dir.mkdir(parents=True, exist_ok=True)

    if not paths.entries_path.exists():
        paths.entries_path.write_text("[]", encoding="utf-8")

    if not paths.meta_path.exists():
        # you can add defaults here later
        paths.meta_path.write_text("{}", encoding="utf-8")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # preserve corrupt file
        backup = path.with_suffix(path.suffix + ".corrupt")
        path.replace(backup)
        path.write_text(json.dumps(default, indent=2,
                        ensure_ascii=False), encoding="utf-8")
        return default


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(
        obj, indent=2, ensure_ascii=False), encoding="utf-8")


def load_entries(paths: Paths) -> list[dict[str, Any]]:
    ensure_storage(paths)
    entries = load_json(paths.entries_path, default=[])
    if isinstance(entries, list):
        return entries
    return []


def save_entries(paths: Paths, entries: list[dict[str, Any]]) -> None:
    ensure_storage(paths)
    save_json(paths.entries_path, entries)
