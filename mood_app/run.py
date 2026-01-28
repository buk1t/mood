# mood_app/run.py
from __future__ import annotations

import webview
from pathlib import Path

from .api import API
from .storage import ensure_storage, resolve_paths


def run(app_name: str = "mood", support_dir: Path | None = None) -> None:
    paths = resolve_paths(app_name=app_name, support_dir=support_dir)
    ensure_storage(paths)

    api = API(app_name=app_name, paths=paths)

    index = paths.web_dir / "index.html"
    window = webview.create_window(
        title="mood",
        url=str(index),
        js_api=api,
        width=920,
        height=720,
        resizable=True,
        frameless=False,
    )
    webview.start(private_mode=False)
