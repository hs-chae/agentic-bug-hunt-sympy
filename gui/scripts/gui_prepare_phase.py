#!/usr/bin/env python3
"""Prepare ChatGPT desktop app phase packets for the agentic SymPy harness."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


HARNESS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_ROOT))
RUN_HARNESS_PATH = HARNESS_ROOT / "core" / "agentic_harness.py"

from cas_harness.io import safe_mkdir, safe_write_text
from cas_harness.paths import (
    PathPolicyError,
    display_path,
    ensure_reserved_output_dirs,
    resolve_run_root,
    safe_output_path,
    validate_report_filename,
)


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
        description="Create one Codex app subagent packet for a harness batch phase."
    )
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--sympy-dir", required=True, type=Path)
    parser.add_argument("--batch", default=1, type=int)
    parser.add_argument("--phase", required=True, choices=sorted(PHASE_PLAN))
    parser.add_argument(
        "--model",
        default="gpt-5.6-sol",
        help="ChatGPT app model to use for the subagent packet. Default: gpt-5.6-sol.",
    )
    parser.add_argument("--writeup-report-name", default="technical_report.tex")
    parser.add_argument("--artifact-repo-url", default="")
    parser.add_argument("--latex-engine", default="auto")
    parser.add_argument("--skip-pdf", action="store_true")
    parser.add_argument(
        "--packet-root",
        type=Path,
        default=None,
        help="Default: RUN_ROOT/_work/gui/batch_packets",
    )
    return parser.parse_args()


def rel_or_abs(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def load_json_if_present(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def infer_artifact_title(artifact_dir: Path) -> str:
    readme = artifact_dir / "README.md"
    if readme.is_file():
        for line in readme.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip() or artifact_dir.name
    return artifact_dir.name


def collect_bug_artifacts(harness: Any, run_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    existing = load_json_if_present(run_root / "run.json")
    existing_artifacts = existing.get("bug_artifacts") if existing else None
    if isinstance(existing_artifacts, list) and existing_artifacts:
        return existing, [item for item in existing_artifacts if isinstance(item, dict)]

    artifacts: list[dict[str, Any]] = []
    for artifact_dir in sorted((run_root / "bug-report").glob("bug-*")):
        if not artifact_dir.is_dir():
            continue
        artifact_dir_rel = harness.display_path(artifact_dir, run_root)
        artifacts.append(
            {
                "artifact_dir": artifact_dir_rel,
                "title": infer_artifact_title(artifact_dir),
                "subsystem": "",
                "dedup_verdict": harness.extract_dedup_verdict_from_artifact(artifact_dir)
                or "unclear",
                **harness.bug_artifact_deliverable_paths(run_root, artifact_dir_rel),
            }
        )
    return existing, artifacts


def build_summary(
    harness: Any,
    *,
    run_root: Path,
    sympy_dir: Path,
    metadata: dict[str, Any],
    artifacts: list[dict[str, Any]],
    existing: dict[str, Any],
) -> dict[str, Any]:
    if existing:
        summary = dict(existing)
        summary["bug_artifacts"] = artifacts
        return summary
    artifacted = len(artifacts)
    novel = sum(1 for bug in artifacts if bug.get("dedup_verdict") == "novel")
    family = sum(
        1 for bug in artifacts if bug.get("dedup_verdict") == "family_known_specific_new"
    )
    unclear = artifacted - novel - family
    return {
        "run_started_utc": "unknown",
        "run_stopped_utc": "unknown",
        "result_dir": str(run_root),
        "sympy_checkout_path": str(sympy_dir),
        "sympy_version": metadata.get("sympy_version"),
        "sympy_file": metadata.get("sympy_file"),
        "sympy_imports_from_checkout": metadata.get("sympy_imports_from_checkout"),
        "sympy_commit": metadata.get("sympy_commit"),
        "python_executable": metadata.get("python_executable"),
        "python_version": metadata.get("python_version"),
        "run_config": {
            "max_bugs": "",
            "max_hours": "",
            "max_empty_passes": "",
            "codex_home": {"note": "ChatGPT desktop app bridge run"},
        },
        "stop_reason": "codex_app_bridge_writeup",
        "bug_outcomes": {
            "candidates_resolved": artifacted,
            "artifacted": artifacted,
            "discarded_total": 0,
            "discarded_by_reason": {
                "rejected_as_duplicate": 0,
                "rejected_as_false_positive": 0,
            },
            "artifacted_by_novelty": {
                "completely_novel": novel,
                "family_known_specific_new": family,
                "unclear_duplicate_status": unclear,
            },
        },
        "root_causes_located": "",
        "pre_existing_artifacts": 0,
        "empty_passes_observed": 0,
        "bug_artifacts": artifacts,
        "rejected_duplicate_candidates": [],
        "iterations": [],
    }


def build_prompt(
    harness: Any,
    *,
    phase: str,
    run_root: Path,
    sympy_dir: Path,
    batch_dir: Path,
    plan_path: Path,
) -> str:
    scratch = batch_dir / "scratch" / phase
    safe_mkdir(run_root, scratch)
    metadata = load_json_if_present(run_root / "run.json")
    if not metadata:
        metadata = harness.collect_sympy_metadata(sympy_dir)

    if phase == "hunter":
        return harness.build_candidate_prompt(
            plan_path,
            sympy_dir,
            run_root,
            scratch,
            run_root / "bug-report",
            run_root / "candidates",
            metadata,
        )
    if phase == "verify":
        return harness.build_verify_prompt(plan_path, sympy_dir, run_root, scratch, metadata)
    if phase == "diagnosis":
        return harness.build_diagnosis_prompt(plan_path, sympy_dir, run_root, scratch, metadata)
    if phase == "dedup":
        return harness.build_dedup_prompt(plan_path, scratch)
    if phase == "artifact":
        return harness.build_artifact_prompt(plan_path, sympy_dir, run_root, scratch, metadata)
    if phase == "writeup":
        return build_writeup_driver_prompt(
            run_root=run_root,
            sympy_dir=sympy_dir,
            plan_path=plan_path,
            packet_root=run_root / "_work" / "gui" / "batch_packets" / "writeup",
        )
    raise ValueError(f"unsupported phase: {phase}")


def build_writeup_driver_prompt(
    *,
    run_root: Path,
    sympy_dir: Path,
    plan_path: Path,
    packet_root: Path,
) -> str:
    python_name = "python" if os.name == "nt" else "python3"
    command = [
        python_name,
        "scripts/gui_writeup_assemble.py",
        "--run-root",
        str(run_root),
        "--sympy-dir",
        str(sympy_dir),
    ]
    command_text = (
        subprocess.list2cmdline(command)
        if os.name == "nt"
        else " ".join(shlex.quote(part) for part in command)
    )
    return "\n".join(
        [
            "# ChatGPT Desktop App Write-up Driver",
            "",
            "You are the ChatGPT desktop app write-up worker for this run.",
            "",
            f"Read the write-up plan at `{plan_path}`. It lists per-bug prompt",
            "files under `per_bug_prompts`.",
            "",
            "For each per-bug prompt, read the prompt file and perform exactly that",
            "write-up task. Write the requested `detailed-analysis.tex` and",
            "`bug-card.tex` files.",
            "",
            "After all per-bug TeX files are written, run:",
            "",
            "```text",
            command_text,
            "```",
            "",
            "If assembly or compilation reports errors, inspect and fix the relevant",
            "TeX files, then rerun the assembler. Stop only when the assembler passes",
            "or after recording a concrete external failure in your final message.",
            "",
            f"Scratch files belong under `{packet_root}` or `_work/writeup/scratch/`.",
            "",
        ]
    )


def output_paths_for_phase(phase: str, plan_path: Path) -> list[str]:
    if phase == "hunter":
        return [str(plan_path)]
    if not plan_path.exists():
        return [f"{plan_path} (missing; create this plan before preparing {phase})"]
    if phase == "writeup":
        plan = load_json_if_present(plan_path)
        outputs = [
            str(item.get("detailed_tex_path", ""))
            for item in plan.get("items", [])
            if isinstance(item, dict)
        ]
        outputs.extend(
            str(item.get("card_tex_path", ""))
            for item in plan.get("items", [])
            if isinstance(item, dict)
        )
        outputs.append(str(plan.get("technical_report_tex", "")))
        return [item for item in outputs if item]
    with plan_path.open(encoding="utf-8") as handle:
        plan = json.load(handle)
    entries = plan.get("candidates") if phase != "artifact" else plan.get("items")
    if not isinstance(entries, list):
        return []
    field_by_phase = {
        "verify": "verify_report_path",
        "diagnosis": "root_cause_path",
        "dedup": "dedup_report_path",
        "artifact": "artifact_status_path",
    }
    field = field_by_phase[phase]
    return [str(item.get(field, "")) for item in entries if isinstance(item, dict)]


def prepare_writeup_plan(
    harness: Any,
    *,
    run_root: Path,
    sympy_dir: Path,
    plan_path: Path,
    packet_root: Path,
    writeup_report_name: str,
    artifact_repo_url: str,
    latex_engine: str,
    skip_pdf: bool,
) -> None:
    metadata = load_json_if_present(run_root / "run.json")
    if not metadata:
        metadata = harness.collect_sympy_metadata(sympy_dir)
    existing, artifacts = collect_bug_artifacts(harness, run_root)
    summary = build_summary(
        harness,
        run_root=run_root,
        sympy_dir=sympy_dir,
        metadata=metadata,
        artifacts=artifacts,
        existing=existing,
    )
    report_root = run_root / "final-report"
    bugs_dir = report_root / "bugs"
    work_dir = run_root / "_work" / "writeup"
    scratch_dir = work_dir / "scratch"
    report_name = validate_report_filename(writeup_report_name)
    report_tex = report_root / report_name
    latex_engine_name, latex_exe = harness.resolve_latex_engine(latex_engine)

    per_bug_prompts: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    prompt_dir = packet_root / "writeup" / "per_bug_prompts"
    safe_mkdir(run_root, prompt_dir)
    for index, bug in enumerate(artifacts, start=1):
        artifact_dir_rel = str(bug.get("artifact_dir", "") or "")
        bug_folder = run_root / artifact_dir_rel if artifact_dir_rel else run_root
        name = Path(artifact_dir_rel).name if artifact_dir_rel else f"bug-{index:03d}"
        bug_out_dir = bugs_dir / name
        safe_mkdir(run_root, bug_out_dir)
        bug_scratch = scratch_dir / name
        detailed_tex = bug_out_dir / "detailed-analysis.tex"
        card_tex = bug_out_dir / "bug-card.tex"
        prompt_path = prompt_dir / f"writeup-bug-{index:03d}-{name}.prompt.md"
        prompt = harness.build_writeup_bug_prompt(
            bug_folder,
            index,
            str(bug.get("title", "")),
            detailed_tex,
            card_tex,
            name,
            bug_scratch,
            harness.build_latex_compile_section(
                latex_engine_name,
                latex_exe,
                detailed_tex,
                bug_scratch / "latex",
                doc_label="the detailed analysis (detailed-analysis.tex)",
            ),
            harness.build_latex_compile_section(
                latex_engine_name,
                latex_exe,
                card_tex,
                bug_scratch / "latex-card",
                doc_label="the bug card (bug-card.tex)",
            ),
            artifact_repo_url,
        )
        safe_write_text(run_root, prompt_path, prompt)
        per_bug_prompts.append(
            {
                "bug_id": index,
                "name": name,
                "prompt_path": display_path(prompt_path, run_root),
                "artifact_dir": artifact_dir_rel,
            }
        )
        items.append(
            {
                "bug_id": index,
                "name": name,
                "artifact_dir": artifact_dir_rel,
                "detailed_tex_path": display_path(detailed_tex, run_root),
                "card_tex_path": display_path(card_tex, run_root),
            }
        )

    safe_write_text(
        run_root,
        plan_path,
        json.dumps(
            {
                "phase": "writeup",
                "run_root": ".",
                "sympy_dir": str(sympy_dir),
                "writeup_report_name": report_name,
                "latex_engine": latex_engine,
                "skip_pdf": skip_pdf,
                "technical_report_tex": display_path(report_tex, run_root),
                "status_path": display_path(work_dir / "writeup_status.json", run_root),
                "per_bug_prompts": per_bug_prompts,
                "items": items,
                "summary": summary,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def write_packet(
    *,
    run_root: Path,
    sympy_dir: Path,
    batch: int,
    phase: str,
    model: str,
    plan_path: Path,
    prompt_path: Path,
    packet_path: Path,
    expected_outputs: list[str],
) -> None:
    lines = [
        f"# ChatGPT Desktop App Batch Packet: batch {batch:03d} {phase}",
        "",
        "Run exactly one ChatGPT desktop app subagent for this packet.",
        "",
        "## Source Of Truth",
        "",
        f"- run_root: `{run_root}`",
        f"- sympy_dir: `{sympy_dir}`",
        f"- phase: `{phase}`",
        f"- model: `{model}`",
        f"- plan_path: `{plan_path}`",
        f"- prompt_to_send: `{prompt_path}`",
        "",
        "## Subagent Instructions",
        "",
        f"Run the subagent with `{model}`. Give it the full contents of",
        "`prompt_to_send` and no extra phase-changing instruction. The subagent",
        "must write only the outputs requested by that prompt plus scratch files",
        "under the phase scratch directory.",
        "",
        "Do not advance to the next phase. After the subagent finishes, run",
        "`scripts/gui_validate_phase.py` for this same phase.",
        "",
        "If validation does not pass, do not end the run or advance. Repair only",
        "this phase's requested outputs, rerun the same phase subagent if needed,",
        "and repeat validation until it passes. Another batch's output is never",
        "required to validate this packet.",
        "",
        "## Expected Outputs",
        "",
    ]
    if expected_outputs:
        lines.extend(f"- `{item}`" for item in expected_outputs)
    else:
        lines.append("- No output paths found in the plan.")
    lines.append("")
    safe_write_text(run_root, packet_path, "\n".join(lines))


def main() -> int:
    args = parse_args()
    try:
        run_root = resolve_run_root(args.run_root)
        ensure_reserved_output_dirs(run_root)
    except PathPolicyError as exc:
        raise SystemExit(str(exc)) from exc
    sympy_dir = args.sympy_dir.resolve()
    try:
        packet_root = safe_output_path(
            run_root,
            args.packet_root or (run_root / "_work" / "gui" / "batch_packets"),
        )
        safe_mkdir(run_root, packet_root)
    except PathPolicyError as exc:
        raise SystemExit(str(exc)) from exc
    batch_dir = run_root / "_work" / f"batch-{args.batch:03d}"
    if args.phase == "writeup":
        plan_path = run_root / "_work" / "writeup" / PHASE_PLAN[args.phase]
    else:
        plan_path = batch_dir / "plans" / PHASE_PLAN[args.phase]

    harness = load_harness()
    if args.phase == "writeup":
        prepare_writeup_plan(
            harness,
            run_root=run_root,
            sympy_dir=sympy_dir,
            plan_path=plan_path,
            packet_root=packet_root,
            writeup_report_name=args.writeup_report_name,
            artifact_repo_url=args.artifact_repo_url,
            latex_engine=args.latex_engine,
            skip_pdf=args.skip_pdf,
        )
    prompt = build_prompt(
        harness,
        phase=args.phase,
        run_root=run_root,
        sympy_dir=sympy_dir,
        batch_dir=batch_dir,
        plan_path=plan_path,
    )
    stem = "writeup" if args.phase == "writeup" else f"batch-{args.batch:03d}-{args.phase}"
    prompt_path = packet_root / f"{stem}.prompt.md"
    packet_path = packet_root / f"{stem}.md"
    safe_write_text(run_root, prompt_path, prompt)
    write_packet(
        run_root=run_root,
        sympy_dir=sympy_dir,
        batch=args.batch,
        phase=args.phase,
        model=args.model,
        plan_path=plan_path,
        prompt_path=prompt_path,
        packet_path=packet_path,
        expected_outputs=output_paths_for_phase(args.phase, plan_path),
    )
    print(f"packet={packet_path}")
    print(f"prompt={prompt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
