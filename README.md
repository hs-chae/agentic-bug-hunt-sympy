# Agentic Bug Hunt: SymPy

A multi-agent harness for autonomously discovering correctness bugs in
[SymPy](https://github.com/sympy/sympy), together with the bugs it has found.

Each candidate passes through a verification gate (an independent agent re-runs
the reproducer against a pinned checkout), a source-level diagnosis, and a
deduplication gate against public sources before it is reported. The result is a
self-contained artifact per bug: a minimal reproducer, root-cause notes, and a
proposed fix with regression tests.

## Layout

- **[`harness/`](harness/)** — the multi-agent bug-hunting pipeline and how to
  run it. See [`harness/README.md`](harness/README.md).
- **[`released_bugs/`](released_bugs/)** — the confirmed bugs, one directory per
  bug, plus paper-facing writeups. See
  [`released_bugs/README.md`](released_bugs/README.md).

## Bugs

`released_bugs/` currently holds 63 confirmed bugs (We (humans) manually checked 63 of them, and all 63 were confirmed as genuine SymPy failures on the latest stable SymPy release (version 1.14.0). On the most recent development branch as of publishing this report, at commit 15e21aca70, 62 of the 63 still reproduced) spanning `solveset`, integration, limits, transforms, statistics, matrices, and special-function singularities. Each `bug-NNN-<slug>/` directory contains a `reproduce_bug.py` reproducer, `root_cause.md`, `dedup_report.md`, related-bug probes, and a proposed fix with tests under `pr/`.
