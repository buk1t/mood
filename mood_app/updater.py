# mood_app/updater.py
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

from .storage import Paths, save_json


def _http_get_json(url: str, timeout: int = 15) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "mood-updater",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8")
    return json.loads(data)


def _download(url: str, dest: Path, timeout: int = 30) -> None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "mood-updater"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        dest.write_bytes(resp.read())


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_installed_version(paths: Paths) -> str | None:
    if not paths.installed_version_path.exists():
        return None
    try:
        obj = json.loads(
            paths.installed_version_path.read_text(encoding="utf-8"))
        return obj.get("version")
    except Exception:
        return None


def _write_installed_version(paths: Paths, version_obj: dict[str, Any]) -> None:
    save_json(paths.installed_version_path, version_obj)


def _atomic_replace(src_dir: Path, dst_dir: Path) -> None:
    """
    Replace dst_dir with src_dir atomically-ish:
    - move dst to backup
    - move src to dst
    - delete backup
    """
    dst_dir.parent.mkdir(parents=True, exist_ok=True)

    backup = dst_dir.with_name(dst_dir.name + ".old")
    if backup.exists():
        shutil.rmtree(backup)

    if dst_dir.exists():
        dst_dir.replace(backup)

    src_dir.replace(dst_dir)

    if backup.exists():
        shutil.rmtree(backup)


def check_for_updates_and_apply(repo_owner: str, repo_name: str, paths: Paths) -> dict[str, Any]:
    """
    Returns:
      { ok: bool, status: "up_to_date"|"updated"|"error", message: str, restart_required?: bool, remote_version?: str }
    """
    try:
        latest = _http_get_json(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest")
        assets = latest.get("assets", [])
        asset = next((a for a in assets if a.get(
            "name") == "mood_update.zip"), None)
        if not asset:
            return {
                "ok": False,
                "status": "error",
                "message": "No mood_update.zip asset found on latest GitHub Release.",
            }

        download_url = asset.get("browser_download_url")
        if not download_url:
            return {"ok": False, "status": "error", "message": "Release asset missing download URL."}

        installed_version = _read_installed_version(paths)

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            zip_path = td_path / "mood_update.zip"
            _download(download_url, zip_path)

            # Read version.json from inside zip before installing
            with zipfile.ZipFile(zip_path, "r") as zf:
                # Expect mood_update/version.json
                try:
                    raw = zf.read("mood_update/version.json").decode("utf-8")
                except KeyError:
                    return {
                        "ok": False,
                        "status": "error",
                        "message": "Zip missing mood_update/version.json",
                    }
                version_obj = json.loads(raw)

            remote_version = str(version_obj.get("version", "")).strip()
            if not remote_version:
                return {"ok": False, "status": "error", "message": "version.json missing version."}

            if installed_version == remote_version:
                return {
                    "ok": True,
                    "status": "up_to_date",
                    "message": f"Already on {installed_version}.",
                    "remote_version": remote_version,
                }

            # Optional checksum verify
            expected_sha = str(version_obj.get("sha256", "")).strip().lower()
            if expected_sha:
                actual_sha = _sha256(zip_path)
                if actual_sha.lower() != expected_sha:
                    return {
                        "ok": False,
                        "status": "error",
                        "message": "Checksum mismatch for mood_update.zip (download corrupted or unexpected).",
                    }

            # Extract zip
            extract_dir = td_path / "extract"
            extract_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)

            root = extract_dir / "mood_update"
            new_web = root / "web"
            new_app_pkg = root / "app" / "mood_app"

            if not new_web.exists() or not (new_web / "index.html").exists():
                return {"ok": False, "status": "error", "message": "Update missing web/ folder."}
            if not new_app_pkg.exists() or not (new_app_pkg / "__init__.py").exists():
                return {"ok": False, "status": "error", "message": "Update missing app/mood_app package."}

            # Stage into temp install locations inside Application Support
            stage_web = paths.support_dir / "_stage_web"
            stage_app = paths.app_dir / "_stage_mood_app"

            if stage_web.exists():
                shutil.rmtree(stage_web)
            if stage_app.exists():
                shutil.rmtree(stage_app)

            shutil.copytree(new_web, stage_web)
            shutil.copytree(new_app_pkg, stage_app)

            # Replace live folders
            _atomic_replace(stage_web, paths.web_dir)
            _atomic_replace(stage_app, paths.app_dir / "mood_app")

            # Write installed_version.json
            _write_installed_version(paths, version_obj)

        return {
            "ok": True,
            "status": "updated",
            "message": f"Updated to {remote_version}. Restart required.",
            "remote_version": remote_version,
            "restart_required": True,
        }

    except Exception as e:
        return {"ok": False, "status": "error", "message": f"Update failed: {e!s}"}
