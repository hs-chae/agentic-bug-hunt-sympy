#!/usr/bin/env python3
"""Advance a Codex app bridge run from one phase to the next plan."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


HARNESS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_ROOT))
RUN_HARNESS_PATH = HARNESS_ROOT / "core" / "agentic_harness.py"

from cas_harness.io import safe_mkdir, safe_write_json
from cas_harness.paths import (
    PathPolicyError,
    display_path,
    ensure_reserved_output_dirs,
    resolve_run_root,
    safe_run_path,
)
from cas_harness.receipts import require_receipt


PHASE_PLAN = {
    "hunter": "candidate_batch.json",
    "verify": "verify_batch.json",
    "diagnosis": "diagnosis_batch.json",
    "dedup": "dedup_batch.json",
    "artifact": "artifact_batch.json",
    "writeup": "gui_writeup_plan.json",
}


def load_harness() -> Any:
    spec = importlib.util.spec_from_file_location("cas_bug_run_harness", RUN_HARNESS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {RUN_HARNESS_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the next harness plan after a Codex app phase passes validation."
    )
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--batch", required=True, type=int)
    parser.add_argument("--phase", required=True, choices=sorted(PHASE_PLAN))
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an already-created next plan.",
    )
    parser.add_argument(
        "--strict-exit",
        action="store_true",
        help="Return a nonzero process exit code when advancement is unsafe.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(run_root: Path, path: Path, payload: Any) -> None:
    safe_write_json(run_root, path, payload)


def resolve_path(raw: str, run_root: Path) -> Path:
    return safe_run_path(run_root, raw)


def candidate_number_from_dir(path: Path) -> int | None:
    match = re.fullmatch(r"candidate-(\d+)", path.name)
    return int(match.group(1)) if match else None


def next_candidate_number(candidates_root: Path) -> int:
    numbers = [
        number
        for child in candidates_root.glob("candidate-*")
        for number in [candidate_number_from_dir(child)]
        if number is not None
    ]
    return max(numbers, default=0) + 1


def ensure_overwritable(path: Path, *, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"{path} already exists; pass --force to overwrite")


def candidate_dir_from_entry(entry: dict[str, Any], run_root: Path) -> Path:
    raw = str(entry.get("candidate_json_path", ""))
    if raw:
        return resolve_path(raw, run_root).parent
    number = int(entry["candidate_number"])
    return run_root / "candidates" / f"candidate-{number:03d}"


def advance_hunter(harness: Any, run_root: Path, batch: int, *, force: bool) -> dict[str, Any]:
    batch_dir = run_root / "_work" / f"batch-{batch:03d}"
    plans_dir = batch_dir / "plans"
    candidate_batch_path = plans_dir / "candidate_batch.json"
    verify_batch_path = plans_dir / "verify_batch.json"
    ensure_overwritable(verify_batch_path, force=force)
    payload = load_json(candidate_batch_path)
    status, candidates, _commands = harness.normalize_hunter_batch(payload)
    if status == "no_candidate" or not candidates:
        return {
            "advanced_from": "hunter",
            "hunter_status": status,
            "next_phase": "hunter",
            "next_batch": batch + 1,
            "candidates": 0,
            "empty_pass": True,
            "note": "No candidates; continue with the next hunter batch or stop at the empty-pass limit.",
        }
    candidates_root = run_root / "candidates"
    safe_mkdir(run_root, candidates_root)

    verify_entries: list[dict[str, Any]] = []
    number = next_candidate_number(candidates_root)
    for candidate in candidates:
        candidate_dir = candidates_root / f"candidate-{number:03d}"
        safe_mkdir(run_root, candidate_dir)
        candidate_json = candidate_dir / "candidate_minimized.json"
        candidate_payload = {**candidate, "status": "candidate"}
        write_json(run_root, candidate_json, candidate_payload)
        verify_entries.append(
            {
                "candidate_number": number,
                "candidate_json_path": display_path(candidate_json, run_root),
                "verify_report_path": display_path(candidate_dir / "verify_report.md", run_root),
                "title": candidate_payload.get("title", ""),
                "subsystem": candidate_payload.get("subsystem", ""),
                "error_signature": candidate_payload.get("error_signature", ""),
            }
        )
        number += 1

    harness.write_verify_batch(verify_batch_path, run_root, verify_entries)
    return {
        "advanced_from": "hunter",
        "hunter_status": status,
        "next_phase": "verify",
        "next_batch": batch,
        "next_plan": display_path(verify_batch_path, run_root),
        "candidates": len(verify_entries),
    }


def advance_verify(harness: Any, run_root: Path, batch: int, *, force: bool) -> dict[str, Any]:
    plans_dir = run_root / "_work" / f"batch-{batch:03d}" / "plans"
    verify_batch_path = plans_dir / "verify_batch.json"
    diagnosis_batch_path = plans_dir / "diagnosis_batch.json"
    ensure_overwritable(diagnosis_batch_path, force=force)
    plan = load_json(verify_batch_path)
    diagnosis_entries: list[dict[str, Any]] = []
    rejected = 0
    for entry in plan.get("candidates", []):
        if not isinstance(entry, dict):
            continue
        report_path = resolve_path(str(entry.get("verify_report_path", "")), run_root)
        recommendation = "continue_but_mark_unclear"
        if report_path.exists():
            _verdict, _confidence, recommendation = harness.parse_verify_front_matter(report_path)
        if recommendation == "reject_as_false_positive":
            rejected += 1
            continue
        candidate_dir = candidate_dir_from_entry(entry, run_root)
        diagnosis_entries.append(
            {
                "candidate_number": entry["candidate_number"],
                "candidate_json_path": entry["candidate_json_path"],
                "root_cause_path": display_path(candidate_dir / "root_cause.md", run_root),
                "title": entry.get("title", ""),
                "subsystem": entry.get("subsystem", ""),
            }
        )
    if not diagnosis_entries:
        return {
            "advanced_from": "verify",
            "next_phase": "hunter",
            "next_batch": batch + 1,
            "candidates": 0,
            "rejected_false_positive": rejected,
            "empty_pass": True,
            "note": "No verified candidates survived; continue with the next hunter batch or stop.",
        }
    harness.write_diagnosis_batch(diagnosis_batch_path, run_root, diagnosis_entries)
    return {
        "advanced_from": "verify",
        "next_phase": "diagnosis",
        "next_plan": display_path(diagnosis_batch_path, run_root),
        "candidates": len(diagnosis_entries),
        "rejected_false_positive": rejected,
    }


def dedup_entry_from_candidate(entry: dict[str, Any], run_root: Path) -> dict[str, Any]:
    candidate_dir = candidate_dir_from_entry(entry, run_root)
    candidate_json = resolve_path(str(entry.get("candidate_json_path", "")), run_root)
    data = load_json(candidate_json) if candidate_json.exists() else {}
    return {
        "candidate_number": entry["candidate_number"],
        "candidate_json_path": display_path(candidate_json, run_root),
        "dedup_report_path": display_path(candidate_dir / "dedup_report.md", run_root),
        "diagnosis_report_path": display_path(candidate_dir / "root_cause.md", run_root),
        "artifact_status_path": display_path(candidate_dir / "artifact_status.json", run_root),
        "title": data.get("title", entry.get("title", "")),
        "subsystem": data.get("subsystem", entry.get("subsystem", "")),
        "error_signature": data.get("error_signature", entry.get("error_signature", "")),
    }


def advance_diagnosis(harness: Any, run_root: Path, batch: int, *, force: bool) -> dict[str, Any]:
    plans_dir = run_root / "_work" / f"batch-{batch:03d}" / "plans"
    diagnosis_batch_path = plans_dir / "diagnosis_batch.json"
    dedup_batch_path = plans_dir / "dedup_batch.json"
    ensure_overwritable(dedup_batch_path, force=force)
    plan = load_json(diagnosis_batch_path)
    dedup_entries = [
        dedup_entry_from_candidate(entry, run_root)
        for entry in plan.get("candidates", [])
        if isinstance(entry, dict)
    ]
    harness.write_candidate_batch_for_dedup(dedup_batch_path, run_root, dedup_entries)
    return {
        "advanced_from": "diagnosis",
        "next_phase": "dedup",
        "next_plan": display_path(dedup_batch_path, run_root),
        "candidates": len(dedup_entries),
    }


def advance_dedup(harness: Any, run_root: Path, batch: int, *, force: bool) -> dict[str, Any]:
    plans_dir = run_root / "_work" / f"batch-{batch:03d}" / "plans"
    dedup_batch_path = plans_dir / "dedup_batch.json"
    artifact_batch_path = plans_dir / "artifact_batch.json"
    ensure_overwritable(artifact_batch_path, force=force)
    plan = load_json(dedup_batch_path)
    bug_report_root = run_root / "bug-report"
    confirmed = harness.existing_artifact_count(bug_report_root)
    artifact_items: list[dict[str, Any]] = []
    rejected = 0
    for entry in plan.get("candidates", []):
        if not isinstance(entry, dict):
            continue
        dedup_report = resolve_path(str(entry.get("dedup_report_path", "")), run_root)
        verdict = "unclear"
        recommendation = "continue_but_mark_unclear"
        if dedup_report.exists():
            verdict, _confidence, recommendation = harness.parse_dedup_front_matter(dedup_report)
        if recommendation == "reject_as_duplicate":
            rejected += 1
            continue
        bug_number = confirmed + len(artifact_items) + 1
        title = str(entry.get("title") or f"candidate-{int(entry['candidate_number']):03d}")
        slug = harness.slugify(title)
        artifact_dir_rel = f"bug-report/bug-{bug_number:03d}-{slug}"
        artifact_items.append(
            {
                **entry,
                "bug_number": bug_number,
                "bug_number_padded": f"{bug_number:03d}",
                "slug": slug,
                "artifact_dir": artifact_dir_rel,
                "artifact_dir_relative": artifact_dir_rel,
                "dedup_verdict": verdict,
                "dedup_recommendation": recommendation,
            }
        )
    if not artifact_items:
        return {
            "advanced_from": "dedup",
            "next_phase": "hunter",
            "next_batch": batch + 1,
            "candidates": 0,
            "rejected_duplicate": rejected,
            "empty_pass": True,
            "note": "No dedup-surviving candidates; continue with the next hunter batch or stop.",
        }
    write_json(
        run_root,
        artifact_batch_path,
        {
            "result_dir": ".",
            "bug_report_root": display_path(bug_report_root, run_root),
            "items": artifact_items,
        },
    )
    return {
        "advanced_from": "dedup",
        "next_phase": "artifact",
        "next_plan": display_path(artifact_batch_path, run_root),
        "candidates": len(artifact_items),
        "rejected_duplicate": rejected,
    }


def advance_artifact(run_root: Path, batch: int) -> dict[str, Any]:
    plan_path = run_root / "_work" / f"batch-{batch:03d}" / "plans" / "artifact_batch.json"
    item_count = 0
    if plan_path.is_file():
        plan = load_json(plan_path)
        if isinstance(plan, dict) and isinstance(plan.get("items"), list):
            item_count = len(plan["items"])
    if item_count == 0:
        return {
            "advanced_from": "artifact",
            "batch": batch,
            "next_phase": "hunter",
            "next_batch": batch + 1,
            "empty_pass": True,
            "note": "No artifacts created; continue with the next hunter batch or stop.",
        }
    return {
        "advanced_from": "artifact",
        "batch": batch,
        "next_phase": "writeup",
        "note": "Artifact validation passed. Continue with the writeup phase or create the next hunter batch.",
    }


def advance_writeup(run_root: Path, batch: int) -> dict[str, Any]:
    status_path = run_root / "_work" / "writeup" / "writeup_status.json"
    status = load_json(status_path) if status_path.exists() else {}
    return {
        "advanced_from": "writeup",
        "batch": batch,
        "next_phase": "complete",
        "status_path": str(status_path),
        "writeup_status": status.get("status", "missing"),
        "writeup_validation": status.get("validation", "missing"),
    }


def write_gui_state(run_root: Path, result: dict[str, Any]) -> Path:
    path = run_root / "_work" / "gui" / "state.json"
    existing = {}
    if path.is_file():
        loaded = load_json(path)
        existing = loaded if isinstance(loaded, dict) else {}
    history = list(existing.get("transition_history", [])) if isinstance(existing.get("transition_history"), list) else []
    history.append(result)
    state = {**result, "transition_history": history[-100:]}
    write_json(run_root, path, state)
    return path


def main() -> int:
    args = parse_args()
    try:
        run_root = resolve_run_root(args.run_root)
        ensure_reserved_output_dirs(run_root)
    except PathPolicyError as exc:
        raise SystemExit(str(exc)) from exc
    harness = load_harness()
    if args.phase == "writeup":
        plan_path = run_root / "_work" / "writeup" / PHASE_PLAN[args.phase]
    else:
        plan_path = run_root / "_work" / f"batch-{args.batch:03d}" / "plans" / PHASE_PLAN[args.phase]
    try:
        require_receipt(run_root, args.phase, args.batch, plan_path)
    except SystemExit as exc:
        result = {
            "advanced": False,
            "status": "needs_validation",
            "phase": args.phase,
            "batch": args.batch,
            "plan_path": str(plan_path),
            "error": str(exc),
            "next_action": "run gui_validate_phase; repair current phase outputs and rerun validation until it passes",
        }
        state_path = write_gui_state(run_root, result)
        print(json.dumps({**result, "state_path": str(state_path)}, indent=2, sort_keys=True))
        return 1 if args.strict_exit else 0
    if args.phase == "hunter":
        result = advance_hunter(harness, run_root, args.batch, force=args.force)
    elif args.phase == "verify":
        result = advance_verify(harness, run_root, args.batch, force=args.force)
    elif args.phase == "diagnosis":
        result = advance_diagnosis(harness, run_root, args.batch, force=args.force)
    elif args.phase == "dedup":
        result = advance_dedup(harness, run_root, args.batch, force=args.force)
    elif args.phase == "artifact":
        result = advance_artifact(run_root, args.batch)
    else:
        result = advance_writeup(run_root, args.batch)
    state_path = write_gui_state(run_root, result)
    print(json.dumps({**result, "state_path": str(state_path)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
