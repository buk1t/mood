# bootstrap/main.py
from __future__ import annotations

import shutil
import sys
from pathlib import Path


APP_NAME = "mood"  # Beckett-coded ✅
REPO_ROOT = Path(__file__).resolve().parents[1]

SRC_WEB_DIR = REPO_ROOT / "web"
SRC_APP_DIR = REPO_ROOT / "mood_app"
SRC_VERSION = REPO_ROOT / "version.json"

SUPPORT_DIR = Path.home() / "Library" / "Application Support" / APP_NAME
SUPPORT_APP_DIR = SUPPORT_DIR / "app"
SUPPORT_WEB_DIR = SUPPORT_DIR / "web"
SUPPORT_DATA_DIR = SUPPORT_DIR / "data"
SUPPORT_VERSION = SUPPORT_DIR / "installed_version.json"

SUPPORT_MOOD_APP_DIR = SUPPORT_APP_DIR / "mood_app"


def ensure_dirs() -> None:
    SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
    SUPPORT_APP_DIR.mkdir(parents=True, exist_ok=True)
    SUPPORT_WEB_DIR.mkdir(parents=True, exist_ok=True)
    SUPPORT_DATA_DIR.mkdir(parents=True, exist_ok=True)


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def first_install_if_needed() -> None:
    """
    If there's no installed app code yet, seed Application Support with the repo's web/ + mood_app/.
    This allows future updates to replace those folders without repackaging the .app.
    """
    if not SUPPORT_MOOD_APP_DIR.exists():
        copy_tree(SRC_APP_DIR, SUPPORT_MOOD_APP_DIR)

    # Always ensure web exists (but don't overwrite if user already has it installed)
    if not (SUPPORT_WEB_DIR / "index.html").exists():
        copy_tree(SRC_WEB_DIR, SUPPORT_WEB_DIR)

    # Seed installed_version.json if missing
    if not SUPPORT_VERSION.exists() and SRC_VERSION.exists():
        shutil.copy2(SRC_VERSION, SUPPORT_VERSION)


def run_installed() -> None:
    """
    Import and run the installed app from Application Support.
    """
    # Make sure we import the installed mood_app, not the repo version
    sys.path.insert(0, str(SUPPORT_APP_DIR))

    from mood_app.run import run  # type: ignore
    run(app_name=APP_NAME, support_dir=SUPPORT_DIR)


if __name__ == "__main__":
    ensure_dirs()
    first_install_if_needed()
    run_installed()
