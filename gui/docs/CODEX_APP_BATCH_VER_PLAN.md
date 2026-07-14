# Agentic SymPy ChatGPT App Batch Plan

This branch keeps the workflow batch-aligned: one ChatGPT app subagent handles
one phase for one batch.

## Phase Contract

1. `hunter` writes `candidate_batch.json`.
2. `verify` writes one `verify_report.md` per candidate.
3. `diagnosis` writes one `root_cause.md` per surviving candidate.
4. `dedup` writes one `dedup_report.md` per surviving candidate.
5. `artifact` writes accepted `bug-report/bug-*` bundles with
   `reproduce_bug.py` and `related_bugs.py`.
6. `writeup` writes per-bug TeX and assembles the final technical report.

## Transition Contract

Every phase must pass validation before advancement. Advancement checks a
receipt that binds:

- phase
- batch
- plan path
- plan hash
- validation result

If the receipt is missing, stale, or failing, advancement returns
`status: needs_validation` and the run remains active. Run validation, repair
only the current phase outputs when it reports `status: needs_repair`, and retry
validation until it passes before advancing.

## Empty Batch Contract

- No hunter candidates: go to the next hunter batch or terminal state.
- No verified survivors: go to the next hunter batch or terminal state.
- No dedup survivors: go to the next hunter batch or terminal state.
- Empty downstream plans are not normal progress.

## Output Contract

Public outputs are sanitized and relative. Private outputs stay under `_work/`
or `run.local.json`.
