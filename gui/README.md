# Agentic Bug Hunt SymPy ChatGPT App Harness

This directory is the ChatGPT desktop app bridge for the GPT-5.6 SymPy
bug-hunt pipeline. It runs natively in Windows PowerShell without WSL, and also
runs on macOS and Linux. It is independent of the upstream `harness/` tree: all
GUI scripts, prompts, helpers, and compatibility code live under `gui/`.

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

## Automatic Example Prompt

`CHATGPT_APP_EXAMPLE_RUN.txt` is the paste-ready entry point. Codex may start in
any writable parent workspace: the prompt clones the private `gui` branch, uses
that child checkout as the command working directory, creates workspace-local
SymPy and run directories under `gui/_local/`, and follows the original phase
order:

```text
hunter -> verify -> diagnosis -> dedup -> artifact -> writeup
```

The prompt works with native Windows PowerShell without WSL and with native
macOS/Linux shells. It runs `gpt-5.6-sol` App subagents and automatically repairs
the current phase until validation passes. Future-batch output is never required
to validate the current batch.

The two settings near the top are the only normal edits:

```text
HUNTER_BATCHES: 1
GENERATE_PDF: true
```

Change `HUNTER_BATCHES` to `2` for two complete batches before the aggregate
write-up. With `GENERATE_PDF: true`, Codex finds or installs a user-space LaTeX
engine and requires `final-report/technical_report.pdf`.

To disable PDF generation, change only `GENERATE_PDF: true` to
`GENERATE_PDF: false`. Write-up remains enabled and still produces
`final-report/technical_report.tex`; the prompt skips LaTeX-engine installation
and passes `--skip-pdf` to both `gui_prepare_phase.py` and
`gui_writeup_assemble.py`. For a manually shortened copy without this setting,
remove the PDF-engine requirement in step 7 and add `--skip-pdf` to both
write-up commands in step 8. Do not remove the write-up phase itself.

## Layout

```text
gui/
  scripts/
    setup_sympy_target.py
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

## Native Windows Setup

Use the Windows-native agent and PowerShell in the ChatGPT desktop app. Keep the
repository on the Windows filesystem, not under WSL. Install native Git and
Python, open the repository folder in the app, and run from `gui/`:

```powershell
$TargetDir = python scripts/setup_sympy_target.py --base-dir .\_local\sympy-target --no-conda --output path
$RunRoot = [IO.Path]::GetFullPath((Join-Path $PWD ".\_local\sympy-gui-run"))
```

The Python setup helper enables Git long-path support for its commands and
handles paths containing spaces. `_local/` is ignored and stays inside the
opened workspace, which is compatible with the native Windows sandbox. The
Bash setup script is not used on Windows. See the official
[Windows app guide](https://learn.chatgpt.com/docs/windows/windows-app).

## macOS And Linux Setup

Run from this `gui/` directory:

```sh
TARGET_DIR="$(python3 scripts/setup_sympy_target.py --base-dir ./_local/sympy-target --no-conda --output path)"
RUN_ROOT="./_local/sympy-gui-run"
```

Use `--ref <commit-or-tag>` when you need an exact SymPy revision.

## App Phase Loop

For each phase:

```text
prepare -> run the emitted prompt in the ChatGPT app -> validate -> advance
```

Native Windows PowerShell example for batch 1 hunter:

```powershell
python scripts/gui_prepare_phase.py --run-root "$RunRoot" --sympy-dir "$TargetDir" --batch 1 --phase hunter --model gpt-5.6-sol
python scripts/gui_validate_phase.py --run-root "$RunRoot" --sympy-dir "$TargetDir" --batch 1 --phase hunter --json
python scripts/gui_advance_phase.py --run-root "$RunRoot" --batch 1 --phase hunter
```

macOS/Linux example:

```sh
python3 scripts/gui_prepare_phase.py --run-root "$RUN_ROOT" --sympy-dir "$TARGET_DIR" --batch 1 --phase hunter --model gpt-5.6-sol
```

Between prepare and validate, open the emitted prompt packet in the ChatGPT
desktop app and run one subagent with `gpt-5.6-sol`. After the subagent writes
the requested files, validate and advance.

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
python3 scripts/gui_writeup_assemble.py --run-root "$RUN_ROOT" --sympy-dir "$TARGET_DIR"
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

Windows PowerShell:

```powershell
python -m py_compile core/agentic_harness.py scripts/setup_sympy_target.py scripts/gui_prepare_phase.py scripts/gui_validate_phase.py scripts/gui_advance_phase.py scripts/gui_writeup_assemble.py scripts/security_scan.py
python -m unittest discover -s tests -v
python scripts/security_scan.py
```

macOS/Linux:

```sh
python3 -m py_compile core/agentic_harness.py scripts/setup_sympy_target.py scripts/gui_prepare_phase.py scripts/gui_validate_phase.py scripts/gui_advance_phase.py scripts/gui_writeup_assemble.py scripts/security_scan.py
python3 -m unittest discover -s tests -v
python3 scripts/security_scan.py
```
