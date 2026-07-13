# Writeups

This directory holds the **authored, paper-facing writeups** for each bug:

- `bug-card.tex` / `bug-card.pdf` — the one-page bug card.
- `detailed-analysis.tex` / `detailed-analysis.pdf` — the in-depth analysis.

These are written for the paper. They are **not** emitted by the bug-finding
harness, which is why they live here rather than alongside the per-bug
artifacts.

## Layout

Each subfolder name matches a bug directory at the repository root 1:1:

```
writeups/bug-NNN-<slug>/   ->   ../bug-NNN-<slug>/
```

The matching `../bug-NNN-<slug>/` directory contains the harness-emitted
artifacts for the same bug (reproducer, root-cause notes, dedup report, related
bugs, README, and the PR with tests).

## Building

The `.tex` files are self-contained — they reference no external inputs,
figures, or bibliographies — and compile directly with `pdflatex`:

```bash
pdflatex bug-card.tex
pdflatex detailed-analysis.tex
```
