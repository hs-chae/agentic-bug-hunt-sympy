#!/usr/bin/env python3
"""Assemble and validate the Codex App write-up deliverable.

This script performs the deterministic half of the original write-up phase.
Codex App subagents write the per-bug TeX files; this script splices them into
the standalone technical report, validates the structure, optionally compiles
the PDF, and updates run.json/README.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any


HARNESS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_ROOT))
RUN_HARNESS_PATH = HARNESS_ROOT / "core" / "agentic_harness.py"

from cas_harness.io import safe_mkdir, safe_write_json, safe_write_text
from cas_harness.paths import (
    PathPolicyError,
    display_path,
    ensure_reserved_output_dirs,
    resolve_run_root,
    safe_output_path,
    safe_run_path,
    validate_report_filename,
)
from cas_harness.privacy import make_private_summary, make_public_summary


def load_harness() -> Any:
    spec = importlib.util.spec_from_file_location("cas_bug_run_harness", RUN_HARNESS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {RUN_HARNESS_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Assemble final-report/technical_report.tex after App write-up packets."
    )
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--sympy-dir", required=True, type=Path)
    parser.add_argument("--writeup-report-name", default="technical_report.tex")
    parser.add_argument("--latex-engine", default="auto")
    parser.add_argument("--skip-pdf", action="store_true")
    parser.add_argument(
        "--strict-exit",
        action="store_true",
        help="Return a nonzero process exit code when generated write-up outputs need repair.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(run_root: Path, path: Path, payload: Any) -> None:
    safe_write_json(run_root, path, payload)


def write_public_readme(run_root: Path, public: dict[str, Any]) -> None:
    writeup = public.get("writeup") if isinstance(public.get("writeup"), dict) else {}
    outcomes = public.get("bug_outcomes") if isinstance(public.get("bug_outcomes"), dict) else {}
    lines = [
        "# Agentic SymPy Codex App Run",
        "",
        "This directory contains sanitized public outputs from a Codex App harness run.",
        "",
        "## Target",
        "",
        f"- SymPy version: `{public.get('sympy_version', 'unknown')}`",
        f"- SymPy commit: `{public.get('sympy_commit', 'unknown')}`",
        "",
        "## Outcomes",
        "",
        f"- Artifacts: `{outcomes.get('artifacted', len(public.get('bug_artifacts', [])))}`",
        f"- Stop reason: `{public.get('stop_reason', 'unknown')}`",
        "",
        "## Write-up",
        "",
        f"- TeX: `{writeup.get('tex_path', 'missing')}`",
        f"- PDF status: `{writeup.get('pdf_status', 'unknown')}`",
    ]
    if writeup.get("pdf_path"):
        lines.append(f"- PDF: `{writeup['pdf_path']}`")
    lines.extend(
        [
            "",
            "Private scratch files, raw prompts, logs, local paths, and account telemetry are not part of this public summary.",
            "",
        ]
    )
    safe_write_text(run_root, run_root / "README.md", "\n".join(lines))


def main() -> int:
    args = parse_args()
    try:
        run_root = resolve_run_root(args.run_root)
        ensure_reserved_output_dirs(run_root)
    except PathPolicyError as exc:
        raise SystemExit(str(exc)) from exc
    harness = load_harness()
    plan_path = run_root / "_work" / "writeup" / "gui_writeup_plan.json"
    if not plan_path.is_file():
        raise SystemExit(f"missing write-up plan: {plan_path}")
    plan = load_json(plan_path)
    summary = plan.get("summary")
    if not isinstance(summary, dict):
        raise SystemExit(f"{plan_path} has no summary object")

    accepted = summary.get("bug_artifacts", [])
    if not isinstance(accepted, list):
        raise SystemExit(f"{plan_path} summary.bug_artifacts is not a list")

    report_root = run_root / "final-report"
    bugs_dir = report_root / "bugs"
    work_dir = run_root / "_work" / "writeup"
    log_dir = work_dir / "logs"
    report_status_path = work_dir / "writeup_status.json"
    try:
        report_name = validate_report_filename(args.writeup_report_name)
    except PathPolicyError as exc:
        raise SystemExit(str(exc)) from exc
    report_tex_path = safe_run_path(run_root, f"final-report/{report_name}", allowed_subtree="final-report")
    for directory in (report_root, bugs_dir, log_dir):
        safe_mkdir(run_root, directory)

    bug_entries: list[dict[str, Any]] = []
    bug_texs: list[Path] = []
    validation_errors: list[str] = []
    bug_bodies: list[str] = []
    for index, bug in enumerate(accepted, start=1):
        artifact_dir_rel = str(bug.get("artifact_dir", "") or "")
        name = Path(artifact_dir_rel).name if artifact_dir_rel else f"bug-{index:03d}"
        bug_out_dir = bugs_dir / name
        detailed_tex = bug_out_dir / "detailed-analysis.tex"
        card_tex = bug_out_dir / "bug-card.tex"
        entry: dict[str, Any] = {
            "bug_id": index,
            "name": name,
            "title": bug.get("title", ""),
            "artifact_dir": artifact_dir_rel,
            "dir": display_path(bug_out_dir, run_root),
            "detailed_tex_path": display_path(detailed_tex, run_root),
            "card_tex_path": display_path(card_tex, run_root),
            "source": "codex_app",
        }
        errors = harness.validate_bug_tex(detailed_tex) + harness.validate_bug_card(card_tex)
        if errors:
            entry["validation"] = "failed"
            entry["validation_errors"] = errors
            validation_errors.extend(f"{name}: {error}" for error in errors)
        else:
            body = harness.extract_tex_body(
                detailed_tex.read_text(encoding="utf-8", errors="replace")
            )
            if "\\documentclass" in body or "\\begin{document}" in body:
                error = "could not extract a clean document body"
                entry["validation"] = "failed"
                entry["validation_errors"] = [error]
                validation_errors.append(f"{name}: {error}")
            else:
                entry["validation"] = "passed"
                bug_bodies.append(body)
        bug_entries.append(entry)
        bug_texs.append(detailed_tex)

    safe_write_text(
        run_root,
        report_tex_path,
        harness.build_standalone_technical_report(
            summary,
            harness.build_technical_report_fragment(summary, bug_bodies),
        ),
    )

    validation_errors += harness.validate_standalone_tex(
        report_tex_path,
        label="technical_report.tex",
        required_headings=("\\subsection{Scope}", "\\subsection{Bug Outcomes}"),
    )

    result: dict[str, Any] = {
        "tex_path": display_path(report_tex_path, run_root),
        "status_path": display_path(report_status_path, run_root),
        "bugs_dir": display_path(bugs_dir, run_root),
        "bug_count": len(accepted),
        "per_bug": bug_entries,
        "bug_reports": len(bug_bodies),
        "technical_report_finalize_status": "codex_app_subagent",
        "writeup_status": "report_created",
        "writeup_validation": "passed" if not validation_errors else "failed",
    }
    if validation_errors:
        result["writeup_validation_errors"] = validation_errors

    if args.skip_pdf:
        result["pdf_status"] = "skipped"
    else:
        compile_log = log_dir / "technical_report_compile.log"
        compile_outdir = work_dir / "compile"
        pdf_status, engine, pdf_path = harness.compile_tex_to_pdf(
            report_tex_path,
            args.latex_engine,
            compile_log,
            outdir=compile_outdir,
        )
        if pdf_path is not None and pdf_path.is_file():
            deliverable_pdf = safe_output_path(run_root, report_root / pdf_path.name)
            shutil.copy2(pdf_path, deliverable_pdf)
            pdf_path = deliverable_pdf
        result["pdf_status"] = pdf_status
        result["pdf_engine"] = engine
        result["pdf_compile_log"] = display_path(compile_log, run_root)
        if pdf_path is not None:
            result["pdf_path"] = display_path(pdf_path, run_root)

    result["deliverables"] = {
        "technical_report_tex": display_path(report_tex_path, run_root),
        "technical_report_pdf": result.get("pdf_path"),
        "per_bug_dir": [display_path(bugs_dir / e["name"], run_root) for e in bug_entries],
        "per_bug_detailed_tex": [display_path(t, run_root) for t in bug_texs if t.is_file()],
        "per_bug_card_tex": [
            display_path(bugs_dir / e["name"] / "bug-card.tex", run_root)
            for e in bug_entries
            if (bugs_dir / e["name"] / "bug-card.tex").is_file()
        ],
    }

    status = {
        "status": result["writeup_status"],
        "validation": result["writeup_validation"],
        "tex_path": result["tex_path"],
        "bug_reports": result["bug_reports"],
        "errors": validation_errors,
    }
    write_json(run_root, report_status_path, status)

    summary["writeup"] = result
    summary["run_stopped_utc"] = dt.datetime.now(dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    public_summary = make_public_summary(summary, run_root)
    private_summary = make_private_summary(summary)
    write_json(run_root, run_root / "run.json", public_summary)
    write_json(run_root, run_root / "run.local.json", private_summary)
    write_public_readme(run_root, public_summary)
    bad_pdf = result.get("pdf_status") in {"failed", "error"}
    if validation_errors or bad_pdf:
        result["status"] = "needs_repair"
    else:
        result["status"] = "passed"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if args.strict_exit and (validation_errors or bad_pdf) else 0


if __name__ == "__main__":
    raise SystemExit(main())
