# Released bugs

This repository collects the bugs found by the harness, one directory per bug.

## Directory contract

- **`bug-NNN-<slug>/`** — the **harness artifact** for each bug, i.e. what the
  bug-finding harness actually produces: the reproducer
  (`reproduce_bug.py`), root-cause notes (`root_cause.md`), the dedup report
  (`dedup_report.md`), related-bug probes (`related_bugs.py`), a `README.md`,
  and the proposed fix as a PR with tests under `pr/`.

- **`writeups/bug-NNN-<slug>/`** — the **authored, paper-facing writeups** for
  the same bug (`bug-card` and `detailed-analysis`, as `.tex` + built `.pdf`).
  These are written for the paper and are not emitted by the harness.

Folder names under `writeups/` match the bug directories at the root 1:1, so the
writeup for any bug is at `writeups/<same-name>/`. Keeping the two kinds of
content separate makes the boundary between automated harness output and
hand-authored paper material explicit and auditable.
