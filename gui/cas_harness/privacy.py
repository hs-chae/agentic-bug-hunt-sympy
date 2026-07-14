"""Public/private summary sanitization."""

from __future__ import annotations

from pathlib import Path
from typing import Any


PUBLIC_KEYS = {
    "run_started_utc",
    "run_stopped_utc",
    "sympy_version",
    "sympy_commit",
    "sympy_imports_from_checkout",
    "python_version",
    "stop_reason",
    "bug_outcomes",
    "root_causes_located",
    "empty_passes_observed",
    "bug_artifacts",
    "writeup",
}

PRIVATE_KEYS = {
    "result_dir",
    "sympy_checkout_path",
    "sympy_file",
    "python_executable",
    "run_config",
    "commands_run",
    "token_usage",
    "codex_home",
}


def _rel(path: Any, run_root: Path) -> str | None:
    if not path:
        return None
    p = Path(str(path))
    if not p.is_absolute():
        return str(p)
    try:
        return str(p.resolve(strict=False).relative_to(run_root.resolve()))
    except ValueError:
        return None


def sanitize_bug_artifact(item: Any, run_root: Path) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {}
    out: dict[str, Any] = {}
    for key in ("title", "subsystem", "dedup_verdict", "validation_status"):
        if key in item:
            out[key] = item[key]
    artifact_dir = item.get("artifact_dir") or item.get("artifact_dir_relative")
    rel = _rel(artifact_dir, run_root)
    if rel:
        out["artifact_dir"] = rel
    for key, value in item.items():
        if key.endswith("_path") or key.endswith("_tex") or key.endswith("_pdf"):
            rel_value = _rel(value, run_root)
            if rel_value:
                out[key] = rel_value
    return out


def sanitize_writeup(writeup: Any, run_root: Path) -> dict[str, Any]:
    if not isinstance(writeup, dict):
        return {}
    out: dict[str, Any] = {}
    for key in ("pdf_status", "writeup_status", "writeup_validation", "bug_count", "bug_reports"):
        if key in writeup:
            out[key] = writeup[key]
    for key in ("tex_path", "pdf_path", "bugs_dir"):
        rel = _rel(writeup.get(key), run_root)
        if rel:
            out[key] = rel
    return out


def make_public_summary(summary: dict[str, Any], run_root: Path) -> dict[str, Any]:
    public = {key: summary[key] for key in PUBLIC_KEYS if key in summary}
    public["bug_artifacts"] = [
        sanitize_bug_artifact(item, run_root) for item in summary.get("bug_artifacts", [])
        if isinstance(item, dict)
    ]
    if "writeup" in public:
        public["writeup"] = sanitize_writeup(public["writeup"], run_root)
    return public


def make_private_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in summary.items() if key in PRIVATE_KEYS or key not in PUBLIC_KEYS}
