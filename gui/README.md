# Agentic Bug Hunt SymPy App Harness

This directory is the Codex App bridge for the GPT-5.6 SymPy bug-hunt
pipeline. It is independent of the upstream `harness/` tree: all GUI scripts,
prompts, helpers, and compatibility code live under this `gui/` directory.

It keeps the agentic repo's artifact contract:

- target bugs are SymPy correctness failures,
- each accepted bundle uses `reproduce_bug.py` and `related_bugs.py`,
- final write-up output is `final-report/technical_report.tex`, with PDF when
  a TeX engine is available,
- the deterministic bridge scripts validate each App subagent output before the
  run state advances.

The model used for App subagents should be `gpt-5.6-sol` unless you intentionally
choose another GPT-5.6 tier. The bridge scripts themselves do not invoke a model;
they prepare packets, validate files, and update run state.

## Layout

```text
gui/
  scripts/
    setup_sympy_target.sh
    gui_prepare_phase.py
    gui_validate_phase.py
    gui_advance_phase.py
    gui_writeup_assemble.py
    security_scan.py
  cas_harness/
  core/
  prompts/
  tests/
```

`core/agentic_harness.py` is a private compatibility copy used only by this GUI
pipeline for shared artifact and report helpers. The App entry points are the
`gui_*` scripts.

## Setup

Run from this `gui/` directory:

```sh
TARGET_DIR="$(scripts/setup_sympy_target.sh --base-dir ../sympy-gui-target --no-conda | tail -n1 | sed 's/^TARGET_DIR=//')"
RUN_ROOT="../sympy-gui-run"
```

Use `--ref <commit-or-tag>` with `setup_sympy_target.sh` when you need an exact
SymPy revision.

## App Phase Loop

For each phase:

```text
prepare -> run the emitted prompt in Codex App -> validate -> advance
```

Example for batch 1 hunter:

```sh
python3 scripts/gui_prepare_phase.py --run-root "$RUN_ROOT" --sympy-dir "$TARGET_DIR" --batch 1 --phase hunter --model gpt-5.6-sol
```

Open the emitted prompt packet in Codex App and run one subagent with
`gpt-5.6-sol`. After the subagent writes the requested files:

```sh
python3 scripts/gui_validate_phase.py --run-root "$RUN_ROOT" --sympy-dir "$TARGET_DIR" --batch 1 --phase hunter --json
python3 scripts/gui_advance_phase.py --run-root "$RUN_ROOT" --batch 1 --phase hunter
```

Repeat for `verify`, `diagnosis`, `dedup`, and `artifact` as directed by the
advance output. A validation mismatch is an automatic repair state: fix only the
current phase files and rerun validation until it passes before advancing. A
phase never requires output from a later batch.

For write-up:

```sh
python3 scripts/gui_prepare_phase.py --run-root "$RUN_ROOT" --sympy-dir "$TARGET_DIR" --batch 1 --phase writeup --model gpt-5.6-sol
python3 scripts/gui_writeup_assemble.py --run-root "$RUN_ROOT"
```

## Outputs

`RUN_ROOT` is the source of truth:

```text
RUN_ROOT/
  run.json
  run.local.json
  candidates/
  bug-report/
  final-report/
  _work/
```

`run.json`, `candidates/`, `bug-report/`, and `final-report/` are the public
surface. `_work/` and `run.local.json` are local diagnostics.

Accepted bug bundles are under `bug-report/bug-*` and include:

- `README.md`
- `reproduce_bug.py`
- `related_bugs.py`
- `root_cause.md`
- `dedup_report.md`
- `pr/README.md`
- `pr/tests/test_*.py`

## Local Checks

```sh
python3 -m py_compile core/agentic_harness.py scripts/gui_prepare_phase.py scripts/gui_validate_phase.py scripts/gui_advance_phase.py scripts/gui_writeup_assemble.py scripts/security_scan.py
python3 -m unittest discover -s tests -v
python3 scripts/security_scan.py
```
