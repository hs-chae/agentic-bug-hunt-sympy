# Codex App Harness Release Hardening Plan

This file is the required fix plan before the Codex App harness is treated as
public, merge-ready, or safe for non-local users.

This is an internal remediation document. It intentionally names deprecated
commands and private-output markers so implementers can remove or scan for them.
Do not include this file in public release scans or maintainer-facing bundles.

The goal is not only to make the happy path work. The goal is to make the
pipeline hard to misuse, safe to publish, and testable after future edits.

Do not push any implementation branch until the owner explicitly allows it.

## Release Decision

Current status: not release-ready.

Private experimentation can continue after the P0 fixes pass locally. Public
release should wait until all P0 and P1 items below have tests.

## Implementation Progress

- [x] Path safety helpers implemented and wired into GUI scripts.
- [x] Validation receipts required before advancing.
- [x] Symlinked run/output directories are rejected by App scripts.
- [x] Validation receipts include validated output manifests.
- [x] Empty/no-candidate batches route to next hunter or terminal state.
- [x] Public/private output split implemented.
- [x] `AGENTS.md` added.
- [x] Public docs/skill no longer instruct old runner usage.
- [x] Legacy runner quarantined away from the public App surface.
- [x] Tests added for path safety, validation, state flow, privacy, and scans.
- [x] Security/privacy scan added.
- [x] Full local checks passed.
- [x] Commit created and pushed after explicit owner request.

## Required End State

The release branch must satisfy all of the following:

- The Codex App path is the only public workflow.
- No user-facing docs instruct anyone to run `codex exec`.
- No user-facing docs instruct anyone to run `scripts/run_harness.py`.
- Old CLI/`codex exec` code is removed from the release surface, or moved under
  a clearly private/legacy area that is not imported by the App bridge.
- Every agent-authored path is contained under `RUN_ROOT`.
- A phase cannot advance unless validation for that exact phase and batch passed.
- Empty/no-candidate batches do not flow through verify, diagnosis, dedup,
  artifact, and write-up.
- Public outputs contain no private paths, Codex account data, raw prompts, raw
  logs, command transcripts, or token/rate-limit telemetry.
- `AGENTS.md` exists and states the harness invariants.
- Tests cover path safety, state transitions, validation, privacy, and security
  scans.
- A smoke run proves the App bridge still works from hunter through write-up.

## P0: Must Fix First

### 1. Path Safety

Problem:

Agent-written plans and write-up arguments can currently create paths outside
`RUN_ROOT` or outside `final-report/`.

Required implementation:

- Add one shared path-policy module.
- Reject absolute output paths in plans.
- Reject `..` path components in all plan-authored paths.
- Resolve paths and verify containment before reading, writing, or copying.
- Reject write-up report names that are paths rather than filenames.
- Reject symlink escapes.

Required API:

```python
def validate_report_filename(raw: str) -> str:
    """Return a safe filename like technical_report.tex, or raise."""

def safe_run_path(run_root: Path, raw: str, *, allowed_subtree: str | None = None) -> Path:
    """Return a resolved path contained in RUN_ROOT or a named subtree."""
```

Acceptance tests:

- `../../outside.tex` is rejected as a write-up report name.
- `/tmp/outside.tex` is rejected as a write-up report name.
- `technical_report.tex` writes only to `RUN_ROOT/final-report/`.
- Absolute artifact paths are rejected.
- `../artifact` paths are rejected.
- Symlink escape paths are rejected.

### 2. Validation Before Advancing

Problem:

`gui_advance_phase.py` can advance phases even if the phase output is missing,
malformed, or never validated.

Required implementation:

- `gui_validate_phase.py` must write a validation receipt on success.
- `gui_advance_phase.py` must refuse to advance without that receipt.
- The receipt must bind to phase, batch, plan path, plan hash, and validated
  output file hashes/sizes.
- Advancement must fail closed: no receipt, stale receipt, wrong batch, wrong
  phase, changed plan, or changed/missing validated output means no transition.

Validation receipt shape:

```json
{
  "schema_version": 1,
  "phase": "verify",
  "batch": 1,
  "ok": true,
  "plan_path": "_work/batch-001/plans/verify_batch.json",
  "plan_sha256": "...",
  "validated_outputs": [
    {
      "path": "candidates/candidate-001/verify_report.md",
      "type": "file",
      "size": 123,
      "sha256": "..."
    }
  ],
  "validated_at_utc": "...",
  "errors": []
}
```

Acceptance tests:

- Artifact phase cannot advance without an artifact plan.
- Artifact phase cannot advance without a passed artifact validation receipt.
- Write-up cannot complete without `writeup_status.json`.
- Write-up cannot complete if PDF was required but missing.
- A changed plan invalidates the old receipt.
- A changed or missing validated output invalidates the old receipt.
- Symlinked `RUN_ROOT`, `_work`, `candidates`, `bug-report`, or `final-report`
  is rejected before output generation or advancement.

### 3. Public/Private Output Split

Problem:

Generated public files can expose absolute local paths, Python executable paths,
Codex home paths, rollout/session metadata, token usage, command transcripts,
and private scratch/log paths.

Required implementation:

- Split run metadata into public and private files:
  - `run.json`: public, allowlisted, path-sanitized.
  - `run.local.json`: private, gitignored, local diagnostics only.
- Generate public `README.md` only from public `run.json`.
- Keep `_work/`, raw prompts, raw logs, raw messages, and telemetry private.
- Make Codex telemetry collection opt-in and private.

Public `run.json` may include:

- target project name
- SymPy version
- SymPy commit hash
- Python version string without absolute executable path
- relative bug artifact paths
- validation status
- write-up PDF status
- stop reason

Public `run.json` must not include:

- `/home`, `/Users`, `/ryu`, `/tmp`, or other absolute local paths
- `CODEX_HOME`
- rollout/session filenames
- rate-limit windows
- subscription or account information
- raw command lines
- raw stdout/stderr
- raw prompt text
- private scratch directories

Acceptance tests:

- Public `run.json` contains no absolute paths.
- Public `README.md` contains no absolute paths.
- Public outputs contain no `CODEX_HOME`, `codex exec`, rollout, rate-limit, or
  token telemetry strings.
- Private diagnostics exist only in `run.local.json` or `_work/`.
- `_work/` and `run.local.json` are gitignored.

## P1: Must Fix Before Public Release

### 4. Add `AGENTS.md`

Problem:

The App skill tells Codex to read `AGENTS.md`, but the file is missing.

Required content:

```markdown
# AGENTS.md

## Harness Invariants

- Do not rely on chat history. Re-read `RUN_ROOT` state.
- Do not run `codex exec`.
- Do not run the old CLI runner.
- Use the Codex App bridge flow only.
- Do not advance unless validation passed for the same phase and batch.
- Treat `_work/` and `run.local.json` as private.
- Do not publish absolute paths, raw logs, raw prompts, Codex home paths, or
  token/rate-limit telemetry.
- Keep every output path inside `RUN_ROOT`.
- If a plan is malformed, stop and report the schema error.
```

Acceptance tests:

- The repository root contains `AGENTS.md`.
- The skill can read it.
- It has no private local paths.

### 5. Empty/No-Candidate Batches

Problem:

A hunter batch with no candidates can pass through every downstream phase and
then reach write-up.

Required implementation:

- Track `empty_passes` and `max_empty_passes` in GUI state.
- If hunter returns no candidates, route to the next hunter batch or stop.
- If verify rejects all candidates, route to the next hunter batch or stop.
- If dedup marks all candidates duplicate/known-rejected, route to the next
  hunter batch or stop.
- Do not create empty verify, diagnosis, dedup, artifact, or write-up plans as a
  normal transition.

Acceptance tests:

- `no_candidate` hunter result does not enter verify.
- all-refuted verify result does not enter diagnosis.
- all-duplicate dedup result does not enter artifact.
- empty-pass limit produces a clean terminal state.

### 6. Tests and Privacy Checks

Required test suite:

```text
tests/
  test_paths.py
  test_plan_schemas.py
  test_validate_phase.py
  test_advance_phase.py
  test_empty_batch_flow.py
  test_writeup_assemble_paths.py
  test_public_private_summary.py
  test_security_scan.py
  test_smoke_app_bridge.py
```

Minimum checks:

- Python compile check for all scripts/modules.
- Path traversal negative tests.
- Malformed JSON plan returns structured error, not traceback.
- Validation receipt is required before advancement.
- Public output contains no private paths or telemetry.
- Artifact validation runs the reproducer scripts, not only structure checks.
- Smoke run reaches write-up with a small fixture.

Recommended command:

```sh
python3 -m py_compile scripts/*.py
python3 -m pytest -q
```

### 7. Security Scanning

Add a local release scan that fails on obvious leaks.

Required scanner checks:

- absolute private paths:
  - `/home/`
  - `/Users/`
  - `/ryu/`
  - `/tmp/`
- Codex/account telemetry:
  - `CODEX_HOME`
  - `rollout`
  - `rate_limit`
  - `subscription`
  - `tokens used`
- old execution path:
  - `codex exec`
  - `run_harness.py`
- secrets:
  - `OPENAI_API_KEY`
  - `sk-`
  - `.env`
  - private keys
- generated caches:
  - `__pycache__`
  - `.pytest_cache`
  - `*.pyc`

Important distinction:

- Source files may mention banned strings only in tests that prove the scanner
  catches them.
- Public docs, public run outputs, and release archives must not mention them.

Required commands:

```sh
git status --short
find . -name '__pycache__' -o -name '*.pyc' -o -name '.pytest_cache'
grep -RInE 'codex exec|run_harness\\.py|CODEX_HOME|rollout|rate_limit|subscription|tokens used|/ryu/|/home/|/Users/|/tmp/' \
  README.md AGENTS.md docs .agents scripts prompts tests
```

The scan should be wrapped in a test or script so it can be rerun before every
release package.

## Old Runner and CLI Trace Removal

The release branch must not look like a wrapper around the old CLI.

Required cleanup:

- Remove `codex exec` from user-facing docs.
- Remove `scripts/run_harness.py` from user-facing instructions.
- Remove old CLI examples from `README.md`.
- Remove branch-history language like "batch-ver", "publishable", or internal
  migration notes from public docs.
- Move legacy CLI material to `docs/internal/` or delete it from the release
  branch.
- Stop importing `scripts/run_harness.py` dynamically from GUI scripts. Extract
  shared prompt/rendering/validation helpers into importable App-bridge modules.
- Keep only thin public entry points for the Codex App bridge.

Acceptance grep:

```sh
grep -RInE 'codex exec|scripts/run_harness\\.py|old CLI|publishable|batch-ver' \
  README.md AGENTS.md docs .agents prompts scripts
```

This grep must return nothing in public docs. It may return matches in internal
tests that intentionally check the removal scanner.

## Extra Must-Fix Items

These are not optional if the branch is meant for serious use.

### Schema Validation

Every plan/status file must have a schema or equivalent strict validator.

Must validate:

- root object type
- required fields
- allowed enum values
- confidence range `0..100`
- candidate numbers are positive integers
- paths are relative and contained
- no unknown phase names

Malformed files must return structured JSON errors and nonzero exit, not Python
tracebacks.

### Atomic State Writes

State writes must be atomic.

Required:

- write to temp file
- flush and fsync
- `os.replace`
- lock state transitions with `_work/gui/state.lock`
- keep transition history, not only the latest state

### Interpreter Consistency

The harness must use one recorded Python executable for helper scripts and
artifact validation.

Required:

- Record `python_executable` in private state.
- Use it for prepare, validate, advance, artifact validation, and write-up.
- Do not publish the absolute executable path.

### Setup Safety

Setup must fail loudly if requested dependencies cannot be created.

Required:

- If `--install` or conda environment creation was requested and conda is
  missing, exit nonzero.
- Do not use shell pipelines in README that can turn setup failure into
  `TARGET_DIR=""`.
- Prefer a simple setup command plus explicit printed `TARGET_DIR=...`.

### Artifact Validation Must Execute Evidence

Artifact validation must not only check file existence.

Required:

- Run `reproduce_bug.py`.
- Run `related_bugs.py`.
- Run proposed `pr/tests/*.py` against the pinned checkout when feasible.
- Record whether the regression test fails on the buggy checkout as expected.
- Fail validation if scripts import SymPy from the wrong checkout.

## Final Pipeline Check

Before claiming the pipeline works perfectly, run a clean smoke workflow:

1. Create a fresh `RUN_ROOT`.
2. Use a fresh SymPy checkout.
3. Run one hunter packet through the Codex App bridge.
4. Validate and advance each phase.
5. Produce at least one artifact.
6. Run artifact evidence scripts.
7. Run write-up.
8. Compile `final-report/technical_report.pdf`.
9. Run privacy scan on public outputs.
10. Run full test suite.
11. Confirm `git status --short` contains only intentional source changes.

The final report must include:

- branch name
- commit hash
- SymPy commit hash
- exact test commands
- smoke-run `RUN_ROOT`
- number of artifacts created
- PDF path
- privacy scan result
- known remaining limitations

## Definition of Done

The hardening work is done only when:

- all P0/P1 tests pass,
- public docs no longer mention old CLI/`codex exec` workflow,
- `AGENTS.md` exists,
- public outputs are path-sanitized,
- private outputs are gitignored,
- no phase can advance without validation,
- empty batches route correctly,
- security scan passes,
- a fresh smoke run reaches PDF write-up,
- and no remote push is made without explicit owner approval.
