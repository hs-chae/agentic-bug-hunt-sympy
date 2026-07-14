# Agentic SymPy ChatGPT App Harness

This branch exposes the agentic SymPy bug-hunt workflow through the ChatGPT
desktop app. Use
`gpt-5.6-sol` for App subagents unless you intentionally choose another GPT-5.6
tier.

## Source Of Truth

The source of truth is `RUN_ROOT`:

```text
RUN_ROOT/
  candidates/
  bug-report/
  final-report/
  run.json
  run.local.json
  _work/
```

`run.json`, `bug-report/`, and `final-report/` are the public surface after
sanitization. `run.local.json` and `_work/` are private local diagnostics.

## Control Loop

For each phase, the ChatGPT desktop app performs:

```text
prepare -> spawn subagent -> validate -> advance
```

The deterministic helpers live under `gui/scripts/`:

```text
scripts/gui_prepare_phase.py
scripts/gui_validate_phase.py
scripts/gui_advance_phase.py
scripts/gui_writeup_assemble.py
```

All helpers are Python and support native Windows PowerShell. On Windows, use
`scripts/setup_sympy_target.py`; do not invoke WSL or the Bash setup script.
Store the repository on the Windows filesystem and use native Git and Python.

`gui_validate_phase.py` writes a validation receipt. `gui_advance_phase.py`
refuses to advance without a matching passing receipt whose plan hash and
validated output manifest still match the filesystem.

Validation mismatches are nonterminal. A failed validation returns
`status: needs_repair`; the app should repair the current phase output and
rerun validation instead of ending the run. Validation of one batch never
depends on a later batch.

## Batch Rule

This is the batch-aligned branch. Each phase uses exactly one ChatGPT app
subagent.

## Write-up

`PHASE=writeup` emits per-bug prompts plus a driver packet. The subagent writes
per-bug TeX files, then the deterministic assembler creates and validates the
technical report.

## Release Safety

Before public release on Windows PowerShell, run:

```powershell
python -m unittest discover -s tests -v
python scripts/security_scan.py
```

On macOS/Linux, run:

```sh
python3 -m pytest -q
python3 scripts/security_scan.py
```
