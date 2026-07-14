"""Validation receipts used to gate phase advancement."""

from __future__ import annotations

import datetime as dt
import hashlib
from pathlib import Path
from typing import Any

from .io import load_json, safe_write_json
from .paths import display_path, safe_output_path, safe_run_path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _manifest_entry(path: Path, run_root: Path) -> dict[str, Any]:
    if path.is_dir():
        return {
            "path": display_path(path, run_root),
            "type": "dir",
        }
    stat = path.stat()
    return {
        "path": display_path(path, run_root),
        "type": "file",
        "size": stat.st_size,
        "sha256": sha256_file(path),
    }


def build_manifest(paths: list[Path], run_root: Path) -> list[dict[str, Any]]:
    seen: set[str] = set()
    entries: list[dict[str, Any]] = []
    for path in paths:
        safe_output_path(run_root, path)
        if not path.exists():
            continue
        if path.is_dir():
            candidates = [path, *sorted(p for p in path.rglob("*") if p.exists())]
        else:
            candidates = [path]
        for candidate in candidates:
            safe_output_path(run_root, candidate)
            rel = display_path(candidate, run_root)
            if rel in seen:
                continue
            seen.add(rel)
            entries.append(_manifest_entry(candidate, run_root))
    return entries


def verify_manifest(run_root: Path, manifest: Any) -> list[str]:
    if not isinstance(manifest, list):
        return ["validation receipt has no output manifest"]
    errors: list[str] = []
    for entry in manifest:
        if not isinstance(entry, dict):
            errors.append("validation receipt manifest entry is not an object")
            continue
        rel = entry.get("path")
        kind = entry.get("type")
        if not isinstance(rel, str):
            errors.append("validation receipt manifest entry has no path")
            continue
        try:
            path = safe_run_path(run_root, rel)
        except Exception as exc:
            errors.append(f"{rel}: unsafe manifest path: {exc}")
            continue
        if kind == "dir":
            if not path.is_dir():
                errors.append(f"{rel}: validated directory is missing")
            continue
        if kind != "file":
            errors.append(f"{rel}: unsupported manifest entry type {kind!r}")
            continue
        if not path.is_file():
            errors.append(f"{rel}: validated file is missing")
            continue
        stat = path.stat()
        if entry.get("size") != stat.st_size:
            errors.append(f"{rel}: validated file size changed")
            continue
        if entry.get("sha256") != sha256_file(path):
            errors.append(f"{rel}: validated file hash changed")
    return errors


def receipt_path(run_root: Path, phase: str, batch: int) -> Path:
    return run_root / "_work" / "gui" / "validation" / f"batch-{batch:03d}-{phase}.json"


def write_receipt(
    *,
    run_root: Path,
    phase: str,
    batch: int,
    plan_path: Path,
    ok: bool,
    errors: list[str],
    manifest_paths: list[Path] | None = None,
) -> Path:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "phase": phase,
        "batch": batch,
        "ok": ok,
        "plan_path": display_path(plan_path, run_root),
        "plan_sha256": sha256_file(plan_path) if plan_path.is_file() else None,
        "validated_outputs": build_manifest(manifest_paths or [], run_root) if ok else [],
        "validated_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "errors": errors,
    }
    path = receipt_path(run_root, phase, batch)
    safe_write_json(run_root, path, payload)
    return path


def require_receipt(run_root: Path, phase: str, batch: int, plan_path: Path) -> dict[str, Any]:
    path = receipt_path(run_root, phase, batch)
    if not path.is_file():
        raise SystemExit(f"missing validation receipt: {path}")
    receipt = load_json(path)
    if not isinstance(receipt, dict):
        raise SystemExit(f"validation receipt is not an object: {path}")
    if receipt.get("phase") != phase or receipt.get("batch") != batch:
        raise SystemExit(f"validation receipt does not match {phase} batch {batch}: {path}")
    if receipt.get("ok") is not True:
        raise SystemExit(f"validation receipt is not passing: {path}")
    expected_hash = sha256_file(plan_path) if plan_path.is_file() else None
    if receipt.get("plan_sha256") != expected_hash:
        raise SystemExit(f"validation receipt is stale for plan: {plan_path}")
    manifest_errors = verify_manifest(run_root, receipt.get("validated_outputs"))
    if manifest_errors:
        raise SystemExit(
            "validation receipt is stale for outputs:\n"
            + "\n".join(f"- {error}" for error in manifest_errors)
        )
    return receipt
