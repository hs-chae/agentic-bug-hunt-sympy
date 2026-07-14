#!/usr/bin/env python3
"""Validate Codex app phase outputs before advancing the GUI harness."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


HARNESS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_ROOT))
RUN_HARNESS_PATH = HARNESS_ROOT / "core" / "agentic_harness.py"

from cas_harness.paths import (
    PathPolicyError,
    ensure_reserved_output_dirs,
    resolve_run_root,
    safe_run_path,
)
from cas_harness.receipts import write_receipt

PUBLIC_TEXT_SUFFIXES = {".md", ".py", ".tex", ".txt", ".json"}

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
    parser = argparse.ArgumentParser(description="Validate one GUI/app harness phase.")
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--batch", required=True, type=int)
    parser.add_argument("--phase", required=True, choices=sorted(PHASE_PLAN))
    parser.add_argument("--sympy-dir", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--strict-exit",
        action="store_true",
        help="Return a nonzero process exit code when validation needs repair.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def resolve(path: str, run_root: Path, *, allowed_subtree: str | None = None) -> Path:
    return safe_run_path(run_root, path, allowed_subtree=allowed_subtree)


def require_object(payload: Any, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    if not isinstance(payload, dict):
        return None, [f"{label} is not an object"]
    return payload, []


def require_list(plan: dict[str, Any], key: str) -> tuple[list[Any], list[str]]:
    value = plan.get(key)
    if not isinstance(value, list):
        return [], [f"{key} is not a list"]
    return value, []


def check_confidence(confidence: int | None, label: str) -> list[str]:
    if confidence is None:
        return [f"missing integer {label} confidence"]
    if not 0 <= confidence <= 100:
        return [f"{label} confidence out of range: {confidence}"]
    return []


def validate_hunter(plan_path: Path) -> list[str]:
    errors: list[str] = []
    if not plan_path.is_file():
        return [f"missing hunter output: {plan_path}"]
    try:
        payload = load_json(plan_path)
    except json.JSONDecodeError as exc:
        return [f"invalid JSON in {plan_path}: {exc}"]
    payload, type_errors = require_object(payload, "candidate_batch.json")
    errors.extend(type_errors)
    if payload is None:
        return errors
    if payload.get("status") not in {"candidates", "candidate", "no_candidate"}:
        errors.append(f"unexpected candidate batch status: {payload.get('status')!r}")
    if "candidates" in payload and not isinstance(payload.get("candidates"), list):
        errors.append("candidate_batch.json candidates is not a list")
    return errors


def validate_verify(harness: Any, plan_path: Path, run_root: Path) -> list[str]:
    errors: list[str] = []
    plan = load_json(plan_path)
    plan, type_errors = require_object(plan, "verify_batch.json")
    errors.extend(type_errors)
    if plan is None:
        return errors
    entries, list_errors = require_list(plan, "candidates")
    errors.extend(list_errors)
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("verify candidate entry is not an object")
            continue
        try:
            report = resolve(str(entry.get("verify_report_path", "")), run_root, allowed_subtree="candidates")
        except PathPolicyError as exc:
            errors.append(f"candidate {entry.get('candidate_number', '?')}: {exc}")
            continue
        number = entry.get("candidate_number", "?")
        if not report.is_file():
            errors.append(f"candidate {number}: missing verify report {report}")
            continue
        verdict, confidence, recommendation = harness.parse_verify_front_matter(report)
        if verdict not in {"confirmed", "refuted", "unclear"}:
            errors.append(f"candidate {number}: bad verify verdict {verdict!r}")
        errors.extend(f"candidate {number}: {error}" for error in check_confidence(confidence, "verify"))
        if recommendation not in {
            "continue_to_dedup",
            "reject_as_false_positive",
            "continue_but_mark_unclear",
        }:
            errors.append(f"candidate {number}: bad verify recommendation {recommendation!r}")
    return errors


def validate_diagnosis(harness: Any, plan_path: Path, run_root: Path) -> list[str]:
    errors: list[str] = []
    plan = load_json(plan_path)
    plan, type_errors = require_object(plan, "diagnosis_batch.json")
    errors.extend(type_errors)
    if plan is None:
        return errors
    entries, list_errors = require_list(plan, "candidates")
    errors.extend(list_errors)
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("diagnosis candidate entry is not an object")
            continue
        try:
            report = resolve(str(entry.get("root_cause_path", "")), run_root, allowed_subtree="candidates")
        except PathPolicyError as exc:
            errors.append(f"candidate {entry.get('candidate_number', '?')}: {exc}")
            continue
        number = entry.get("candidate_number", "?")
        if not report.is_file():
            errors.append(f"candidate {number}: missing diagnosis report {report}")
            continue
        status, confidence, _location = harness.parse_diagnosis_front_matter(report)
        if status not in {"located", "narrowed", "inconclusive", "missing", "unclear"}:
            errors.append(f"candidate {number}: bad diagnosis status {status!r}")
        errors.extend(f"candidate {number}: {error}" for error in check_confidence(confidence, "diagnosis"))
    return errors


def validate_dedup(harness: Any, plan_path: Path, run_root: Path) -> list[str]:
    errors: list[str] = []
    plan = load_json(plan_path)
    plan, type_errors = require_object(plan, "dedup_batch.json")
    errors.extend(type_errors)
    if plan is None:
        return errors
    entries, list_errors = require_list(plan, "candidates")
    errors.extend(list_errors)
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("dedup candidate entry is not an object")
            continue
        try:
            report = resolve(str(entry.get("dedup_report_path", "")), run_root, allowed_subtree="candidates")
        except PathPolicyError as exc:
            errors.append(f"candidate {entry.get('candidate_number', '?')}: {exc}")
            continue
        number = entry.get("candidate_number", "?")
        if not report.is_file():
            errors.append(f"candidate {number}: missing dedup report {report}")
            continue
        verdict, confidence, recommendation = harness.parse_dedup_front_matter(report)
        if verdict not in {"novel", "family_known_specific_new", "likely_duplicate", "unclear"}:
            errors.append(f"candidate {number}: bad dedup verdict {verdict!r}")
        errors.extend(f"candidate {number}: {error}" for error in check_confidence(confidence, "dedup"))
        if recommendation not in {
            "continue_to_artifact_generation",
            "reject_as_duplicate",
            "continue_but_mark_unclear",
        }:
            errors.append(f"candidate {number}: bad dedup recommendation {recommendation!r}")
    return errors


def run_artifact_script(path: Path, sympy_dir: Path | None) -> list[str]:
    if sympy_dir is None:
        return []
    env = dict(os.environ)
    env["SYMPY_CHECKOUT_PATH"] = str(sympy_dir)
    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(path.parent),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
    )
    if proc.returncode == 0:
        return []
    return [f"{path}: exited {proc.returncode}; stderr={proc.stderr[-500:]}"]


def sanitize_public_tree(root: Path, replacements: list[tuple[str, str]]) -> None:
    if not root.is_dir():
        return
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in PUBLIC_TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        sanitized = text
        for needle, replacement in replacements:
            if needle:
                sanitized = sanitized.replace(needle, replacement)
        if sanitized != text:
            path.write_text(sanitized, encoding="utf-8")


def public_replacements(run_root: Path, sympy_dir: Path | None) -> list[tuple[str, str]]:
    replacements = [(str(run_root.resolve()), "<RUN_ROOT>")]
    if sympy_dir is not None:
        resolved = sympy_dir.resolve()
        replacements.extend(
            [
                (str(resolved), "<SYMPY_CHECKOUT_PATH>"),
                (resolved.as_posix(), "<SYMPY_CHECKOUT_PATH>"),
            ]
        )
    return replacements


def validate_artifact(harness: Any, plan_path: Path, run_root: Path, sympy_dir: Path | None) -> list[str]:
    errors: list[str] = []
    plan = load_json(plan_path)
    plan, type_errors = require_object(plan, "artifact_batch.json")
    errors.extend(type_errors)
    if plan is None:
        return errors
    try:
        bug_report_root = resolve(str(plan.get("bug_report_root", "bug-report")), run_root, allowed_subtree="bug-report")
    except PathPolicyError as exc:
        errors.append(str(exc))
        return errors
    entries, list_errors = require_list(plan, "items")
    errors.extend(list_errors)
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("artifact item is not an object")
            continue
        try:
            status_path = resolve(str(entry.get("artifact_status_path", "")), run_root, allowed_subtree="candidates")
        except PathPolicyError as exc:
            errors.append(f"candidate {entry.get('candidate_number', '?')}: {exc}")
            continue
        number = entry.get("candidate_number", "?")
        if not status_path.is_file():
            errors.append(f"candidate {number}: missing artifact status {status_path}")
            continue
        try:
            status = load_json(status_path)
        except json.JSONDecodeError as exc:
            errors.append(f"candidate {number}: invalid artifact status JSON: {exc}")
            continue
        if status.get("status") != "artifact_created":
            errors.append(f"candidate {number}: artifact status is {status.get('status')!r}")
            continue
        artifact_dir_raw = str(status.get("artifact_dir", ""))
        try:
            artifact_dir = resolve(artifact_dir_raw, run_root, allowed_subtree="bug-report")
        except PathPolicyError as exc:
            errors.append(f"candidate {number}: {exc}")
            continue
        try:
            candidate_json = resolve(
                str(entry.get("candidate_json_path", "")),
                run_root,
                allowed_subtree="candidates",
            )
            harness.finalize_artifact_bundle_metadata(run_root, status, candidate_json)
        except PathPolicyError as exc:
            errors.append(f"candidate {number}: {exc}")
            continue
        sanitize_public_tree(artifact_dir, public_replacements(run_root, sympy_dir))
        ok, bundle_errors, _artifact_dir = harness.validate_artifact_bundle(
            run_root,
            bug_report_root,
            status,
        )
        if not ok:
            errors.extend(f"candidate {number}: {err}" for err in bundle_errors)
            continue
        reproduce = artifact_dir / "reproduce_bug.py"
        if reproduce.is_file():
            errors.extend(
                f"candidate {number}: {error}" for error in run_artifact_script(reproduce, sympy_dir)
            )
        related = artifact_dir / "related_bugs.py"
        if related.is_file():
            # related_bugs.py is useful supporting evidence, but a transient
            # lookup/import problem there should not block a reproduced artifact.
            run_artifact_script(related, sympy_dir)
    return errors


def validate_writeup(harness: Any, run_root: Path) -> list[str]:
    errors: list[str] = []
    plan_path = run_root / "_work" / "writeup" / PHASE_PLAN["writeup"]
    status_path = run_root / "_work" / "writeup" / "writeup_status.json"
    if not plan_path.is_file():
        return [f"missing write-up plan: {plan_path}"]
    plan = load_json(plan_path)
    plan, type_errors = require_object(plan, "gui_writeup_plan.json")
    errors.extend(type_errors)
    if plan is None:
        return errors
    items, list_errors = require_list(plan, "items")
    errors.extend(list_errors)
    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get("name", "?")
        try:
            detailed = resolve(str(item.get("detailed_tex_path", "")), run_root, allowed_subtree="final-report")
            card = resolve(str(item.get("card_tex_path", "")), run_root, allowed_subtree="final-report")
        except PathPolicyError as exc:
            errors.append(f"{name}: {exc}")
            continue
        errors.extend(f"{name}: {error}" for error in harness.validate_bug_tex(detailed))
        errors.extend(f"{name}: {error}" for error in harness.validate_bug_card(card))
    try:
        report_tex = resolve(str(plan.get("technical_report_tex", "")), run_root, allowed_subtree="final-report")
    except PathPolicyError as exc:
        errors.append(str(exc))
        report_tex = run_root / "final-report" / "missing.tex"
    errors.extend(
        harness.validate_standalone_tex(
            report_tex,
            label="technical_report.tex",
            required_headings=("\\subsection{Scope}", "\\subsection{Bug Outcomes}"),
        )
    )
    if not status_path.is_file():
        errors.append(f"missing write-up status: {status_path}")
    else:
        try:
            status = load_json(status_path)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid write-up status JSON: {exc}")
        else:
            if status.get("status") != "report_created":
                errors.append(f"write-up status is {status.get('status')!r}")
            if status.get("validation") != "passed":
                errors.append(f"write-up validation is {status.get('validation')!r}")
    return errors


def collect_validated_outputs(
    harness: Any,
    phase: str,
    plan_path: Path,
    run_root: Path,
) -> list[Path]:
    outputs: list[Path] = []
    if plan_path.is_file():
        outputs.append(plan_path)
    if phase == "hunter":
        return outputs
    plan = load_json(plan_path)
    if not isinstance(plan, dict):
        return outputs
    if phase == "verify":
        for entry in plan.get("candidates", []):
            if isinstance(entry, dict):
                outputs.append(resolve(str(entry.get("verify_report_path", "")), run_root, allowed_subtree="candidates"))
    elif phase == "diagnosis":
        for entry in plan.get("candidates", []):
            if isinstance(entry, dict):
                outputs.append(resolve(str(entry.get("root_cause_path", "")), run_root, allowed_subtree="candidates"))
    elif phase == "dedup":
        for entry in plan.get("candidates", []):
            if isinstance(entry, dict):
                outputs.append(resolve(str(entry.get("dedup_report_path", "")), run_root, allowed_subtree="candidates"))
    elif phase == "artifact":
        for entry in plan.get("items", []):
            if not isinstance(entry, dict):
                continue
            status_path = resolve(str(entry.get("artifact_status_path", "")), run_root, allowed_subtree="candidates")
            outputs.append(status_path)
            if status_path.is_file():
                status = load_json(status_path)
                if isinstance(status, dict):
                    artifact_dir = status.get("artifact_dir")
                    if isinstance(artifact_dir, str) and artifact_dir:
                        outputs.append(resolve(artifact_dir, run_root, allowed_subtree="bug-report"))
    elif phase == "writeup":
        outputs.append(run_root / "_work" / "writeup" / "writeup_status.json")
        for item in plan.get("items", []):
            if isinstance(item, dict):
                outputs.append(resolve(str(item.get("detailed_tex_path", "")), run_root, allowed_subtree="final-report"))
                outputs.append(resolve(str(item.get("card_tex_path", "")), run_root, allowed_subtree="final-report"))
        outputs.append(resolve(str(plan.get("technical_report_tex", "")), run_root, allowed_subtree="final-report"))
    return outputs


def main() -> int:
    args = parse_args()
    try:
        run_root = resolve_run_root(args.run_root)
        ensure_reserved_output_dirs(run_root)
    except PathPolicyError as exc:
        raise SystemExit(str(exc)) from exc
    if args.phase == "writeup":
        plan_path = run_root / "_work" / "writeup" / PHASE_PLAN[args.phase]
    else:
        plan_path = run_root / "_work" / f"batch-{args.batch:03d}" / "plans" / PHASE_PLAN[args.phase]
    errors: list[str] = []
    if args.phase != "hunter" and not plan_path.is_file():
        errors.append(f"missing plan file: {plan_path}")
    if not errors:
        harness = load_harness()
        try:
            if args.phase == "hunter":
                errors = validate_hunter(plan_path)
            elif args.phase == "verify":
                errors = validate_verify(harness, plan_path, run_root)
            elif args.phase == "diagnosis":
                errors = validate_diagnosis(harness, plan_path, run_root)
            elif args.phase == "dedup":
                errors = validate_dedup(harness, plan_path, run_root)
            elif args.phase == "artifact":
                errors = validate_artifact(harness, plan_path, run_root, args.sympy_dir)
            elif args.phase == "writeup":
                errors = validate_writeup(harness, run_root)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
    manifest_paths: list[Path] = []
    if not errors:
        try:
            manifest_paths = collect_validated_outputs(harness, args.phase, plan_path, run_root)
        except (OSError, json.JSONDecodeError, PathPolicyError) as exc:
            errors.append(f"manifest collection failed: {exc}")

    result = {
        "phase": args.phase,
        "batch": args.batch,
        "plan_path": str(plan_path),
        "ok": not errors,
        "status": "passed" if not errors else "needs_repair",
        "can_advance": not errors,
        "next_action": "advance" if not errors else "repair_current_phase_and_rerun_validation",
        "errors": errors,
    }
    receipt = write_receipt(
        run_root=run_root,
        phase=args.phase,
        batch=args.batch,
        plan_path=plan_path,
        ok=not errors,
        errors=errors,
        manifest_paths=manifest_paths,
    )
    result["receipt_path"] = str(receipt)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("ok" if result["ok"] else "needs_repair")
        for error in errors:
            print(f"- {error}")
    return 1 if args.strict_exit and errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
