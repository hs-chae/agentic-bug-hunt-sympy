"""JSON and state-file I/O helpers."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .paths import safe_output_path


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_json_if_present(path: Path) -> Any:
    if not path.exists():
        return None
    return load_json(path)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def safe_mkdir(run_root: Path, path: Path) -> Path:
    safe_path = safe_output_path(run_root, path)
    safe_path.mkdir(parents=True, exist_ok=True)
    safe_output_path(run_root, safe_path)
    return safe_path


def safe_write_text(run_root: Path, path: Path, text: str) -> None:
    safe_path = safe_output_path(run_root, path)
    safe_mkdir(run_root, safe_path.parent)
    safe_path = safe_output_path(run_root, safe_path)
    atomic_write_text(safe_path, text)


def safe_write_json(run_root: Path, path: Path, payload: Any) -> None:
    safe_write_text(run_root, path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
