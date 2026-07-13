# CAS Bug Codex Harness

This folder contains a multi-agent Codex harness for autonomous SymPy correctness-bug discovery with a verification gate, a deduplication gate, and final LaTeX reporting.

The harness uses:

- a bug-hunting agent that finds and minimizes a batch of candidates without internet search,
- an independent verification agent (no internet search) that re-runs each candidate's reproducer against the pinned checkout and drops false positives before dedup — the only correctness gate in the pipeline,
- a source-level diagnosis agent (no internet search, read-only on the checkout) that locates the SymPy code responsible for each verified bug and writes a `root_cause.md`,
- a deduplication agent that is allowed to search public sources and reviews each surviving candidate in the batch,
- a final artifact-generation phase that creates `bug-report/bug-N-short-title/` bundles under a timestamped result directory only after verification and dedup pass.
- a final write-up phase that produces, per confirmed bug, a folder under `final-report/bugs/` with a compact paper-style `bug-card.tex` and a `detailed-analysis.tex`, plus a single maintainer-facing technical report (`final-report/technical_report.tex`) assembled from the detailed analyses.

The canonical shared bug policy is `prompts/shared_bug_policy.md`.

## Quick Start

Run from this harness directory:

```sh
TARGET_DIR="$(scripts/setup_sympy_target.sh --install | tee /tmp/cas-bug-setup.log | tail -n1 | sed 's/^TARGET_DIR=//')"
```

Then run the harness against that target worktree:

```sh
conda activate sympy-bug-hunt
python3 scripts/run_harness.py --sympy-dir "$TARGET_DIR"
```

Useful options:

```sh
python3 scripts/run_harness.py \
  --sympy-dir "$TARGET_DIR" \
  --output-root ~/cas-bug-results \
  --max-bugs 10 \
  --hours 4 \
  --model gpt-5.6-sol
```

The deduplication agent receives `--search` by default. Use `--no-dedup-search` only if you want a local-only dry run of the dedup phase. The bug-hunting, verification, diagnosis, and final write-up agents never receive search; the bug-hunting, verification, and diagnosis phases intentionally work offline (verification uses code execution and local oracles like `mpmath`/NumPy; diagnosis reads the local SymPy source read-only), and the write-up agent works from the already-recorded artifacts and reports.

If `--model` is omitted, all Codex agents use the default model from your Codex config. Passing `--model` applies the same model to the hunter, verification, diagnosis, dedup, artifact, and write-up agents.

## SymPy Target Setup

For reproducible bug hunting, use a dedicated SymPy checkout or worktree rather than the SymPy package installed in your default Python environment.

Create a locked target checkout:

```sh
scripts/setup_sympy_target.sh
```

Create a locked target checkout and install it into an isolated conda environment:

```sh
scripts/setup_sympy_target.sh --install
conda activate sympy-bug-hunt
python3 scripts/run_harness.py --sympy-dir ~/sympy-bug-hunt/runs/<run-name>
```

Useful setup options:

```sh
scripts/setup_sympy_target.sh \
  --base-dir ~/sympy-bug-hunt \
  --ref origin/master \
  --run-name sympy-run-001 \
  --env-name sympy-bug-hunt \
  --install
```

Use `--create-env` if you want the conda environment created without installing packages. Without `--create-env` or `--install`, setup only prepares the clone/worktree and metadata.

The setup script writes metadata under `~/sympy-bug-hunt/metadata/` (or `<base-dir>/metadata/`), including the exact SymPy commit hash. Use a fresh worktree for each autonomous run so generated files, local tests, and experimental edits are isolated.

By default, setup fetches `origin/master` and creates a timestamped worktree. To run multiple passes against the exact same SymPy version, pin the commit:

```sh
scripts/setup_sympy_target.sh --ref <commit-hash>
```

`--run-name` is optional; omit it to get an automatic timestamped directory name.

## Flow

For each hunter batch:

1. The hunter writes `_work/batch-NNN/plans/candidate_batch.json` with zero or more minimized candidates.
2. The harness splits candidates into `candidates/candidate-NNN/candidate_minimized.json` files.
3. The verification agent re-runs each candidate's reproducer against the pinned checkout and writes one `verify_report.md` per candidate directory. Candidates it refutes as false positives are dropped and never reach dedup; refuted-only batches advance no candidates.
4. The diagnosis agent reads the SymPy checkout to locate the code responsible for each surviving (verified) candidate and writes one `root_cause.md` per candidate directory. This is non-blocking: it never drops a candidate.
5. The dedup agent reviews each surviving candidate in the batch and writes one `dedup_report.md` per candidate directory.
6. If dedup recommends continuing, the artifact agent creates one `bug-report/bug-NNN-short-title/` bundle per accepted candidate in the batch.
7. The harness copies `root_cause.md` (when present) into each bundle, so each accepted bug has a self-contained folder. The hunter's `candidate_minimized.json` and the `artifact_status.json` control signal stay under `candidates/candidate-NNN/` as run scratch and are not copied into the bundle.
8. The harness stops once it has reached or exceeded `--max-bugs`, hit `--hours`, or reached repeated empty passes.
9. The write-up phase produces a single deliverable: the maintainer-facing **technical report** (`final-report/technical_report.tex`), assembled from one detailed per-bug report per confirmed bug. The steps are:

   - a per-bug agent creates one folder `final-report/bugs/bug-NNN-*/` per confirmed bug holding two self-contained deliverables: a compact paper-style counterexample card (`bug-card.tex`) and the full detailed maintainer report (`detailed-analysis.tex`);
   - the harness mechanically assembles the standalone `final-report/technical_report.tex`: a version-anchored scope line, aggregate bug outcomes, then every detailed per-bug analysis spliced in verbatim;
   - when a LaTeX engine is available, a finalize agent runs a compile-and-fix loop on `technical_report.tex` (up to ~6 compile passes before stopping on a benign warning), and every per-bug agent also compiles and fixes both of its own `.tex` files (into a scratch directory; the per-bug PDFs are not kept) before finishing. With no engine available these loops are skipped in favor of a careful self-review;
   - the harness validates that `technical_report.tex` is a complete document and compiles it to PDF when an engine is available.

All run outputs are stored under one timestamped result directory. By default
that directory is created in the current working directory; use `--output-root`
to place it elsewhere. The target SymPy checkout is kept separate from final
results.

Reporting outputs (the candidate decision records, bug bundles, and final
report) live in `candidates/`, `bug-report/`, and `final-report/`. Everything
created only to drive the run — the per-phase handoff plans, raw Codex logs,
captured last messages, and each agent's scratchpad — is consolidated under
`_work/` so it never clutters the reporting directories.

```text
cas-bug-results-YYYYMMDD-HHMMSSZ-sympy-VERSION/
  README.md                        # single human-readable run report
  run.json                         # single machine-readable run record
  candidates/
    candidate-001/                 # per-candidate decision record (reporting)
      candidate_minimized.json
      verify_report.md
      root_cause.md
      dedup_report.md
      artifact_status.json
  bug-report/
    bug-001-short-title/           # confirmed-bug deliverable bundle (reporting)
      README.md
      reproduce_bug.py
      related_bugs.py                 # bugs related to the main reproducer (parametrized cases + numerical cross-check)
      root_cause.md
      dedup_report.md
      pr/
        README.md
        tests/
          test_bug_001_short_title.py
  final-report/                    # final report deliverable (reporting)
    technical_report.tex           # standalone maintainer-facing technical report
    technical_report.pdf           # when a LaTeX engine is available
    bugs/                          # one folder per confirmed bug
      bug-001-short-title/
        bug-card.tex               # compact paper-style counterexample card
        detailed-analysis.tex      # full detailed report (spliced into technical_report.tex)
      bug-002-.../
        bug-card.tex
        detailed-analysis.tex
  _work/                           # intermediate / non-reporting only
    batch-001/
      plans/                       # machine-readable phase handoff files
        candidate_batch.json
        verify_batch.json
        diagnosis_batch.json
        dedup_batch.json
        artifact_batch.json
      logs/                        # raw Codex stdout/stderr per agent
        hunter_candidate.log
        verify_agent.log
        diagnosis_agent.log
        dedup_agent.log
        artifact_agent.log
      messages/                    # Codex -o captured last message per agent
      scratch/                     # per-agent private scratchpads (SCRATCH_DIR)
        hunter/
        verify/
        diagnosis/
        dedup/
        artifact/
    writeup/
      writeup_status.json          # write-up phase-completion marker (intermediate)
      finalize_technical_report_status.json   # technical-report finalize agent's status
      logs/
        writeup_bug_001.log
        writeup_finalize_technical_report.log
        technical_report_compile.log   # harness compile of technical_report.tex
      messages/
      compile/                     # harness PDF compile (.aux/.log byproducts;
                                   # the .pdf is copied into final-report/)
      scratch/                     # per-bug agents (+ their latex/ and latex-card/
                                   # compile dirs) and finalize_technical_report/
```

The runner records the imported SymPy version, SymPy file path, commit hash when
available, Python executable, the `run_config` stopping limits, stop reason, and a
`bug_outcomes` meta-summary (candidates resolved, artifacted, and discarded by
reason, plus the artifacted bugs broken down by deduplication novelty) in
`run.json`. It also validates each artifact bundle before counting it as
confirmed.

## Reading the outputs

Each timestamped result directory holds, in rough order of how readable they are:

- **`final-report/technical_report.pdf`** — the maintainer-facing technical report
  (the single write-up deliverable): a version-anchored scope line, bug outcomes,
  and the complete per-bug reports with reproducers, source-level diagnosis, and
  proposed regression tests. It is assembled from one detailed per-bug analysis
  (`final-report/bugs/*/detailed-analysis.tex`) per confirmed bug. Each bug folder
  also carries a compact paper-style `bug-card.tex`.
- **`bug-report/`** — the canonical per-bug artifacts (`reproduce_bug.py`
  reproducer, `related_bugs.py` covering bugs related to the main reproducer
  (parametrized correctness cases with an inline numerical cross-check), proposed
  pytest regression test, README, PR draft, deduplication notes, and diagnosis).
  These are the reproducibility layer; the report above is generated from them.
- **`README.md`** — the single human-readable run report: run metadata, bug
  outcomes, the accepted-artifact table, discarded candidates, per-iteration trace,
  and the write-up status.
- **`run.json`** — the single machine-readable run record. It carries everything:
  run metadata and config, per-bug outcomes with resolved paths to every per-bug
  deliverable, the full per-iteration pipeline trace, rejected duplicate
  candidates, and (under `writeup`) the technical-report deliverable paths.

## PDF output (no sudo required)

After the write-up phase assembles `final-report/technical_report.tex` (and, when
an engine is available, a finalize agent has compiled and fixed it), the harness
compiles it to PDF using the first available engine of `tectonic`, `latexmk`,
`pdflatex` (override with `--latex-engine`, disable with `--skip-pdf`). The compile
log is `_work/writeup/logs/technical_report_compile.log`, and the PDF path is
recorded under `writeup` in `run.json`.

If no engine is found, the run still succeeds and leaves the `.tex`; install a
TeX engine in user space (no root needed) and re-run, or compile manually. The
simplest option with the bundled conda is:

```sh
conda install -c conda-forge tectonic
```

Tectonic is self-contained and downloads any LaTeX packages the report needs on
first use (it needs network for that initial fetch, then caches). Alternatives
without sudo: TinyTeX (`https://yihui.org/tinytex/`) or a TeX Live user install
with a `$HOME` prefix, both of which provide `pdflatex`/`latexmk`.

Tectonic is a standalone binary, not a Python package — it is never imported and
shares nothing with the SymPy/numpy/mpmath used for bug detection, so it cannot
conflict with them. To keep it out of your main environment entirely, install it
in a dedicated conda env and either activate that env when you run the harness,
or point the harness straight at the binary so no activation is needed:

```sh
conda create -n cas-tex -c conda-forge tectonic
# no activation needed; just point at it:
python scripts/run_harness.py --sympy-dir ... \
  --latex-engine ~/miniconda3/envs/cas-tex/bin/tectonic
```

Engine discovery for `auto`/name checks PATH first, then the directory of the
running Python, `$CONDA_PREFIX/bin`, and common user dirs — so an activated
dedicated env is found automatically. A full path bypasses discovery entirely.

An empty pass means one hunter invocation ended with no plausible minimized candidates. The default `--max-empty-passes 3` stops after three such passes in a row. A candidate rejected by dedup is not counted as an empty pass because the hunter did find a plausible candidate.

## Runner Options

Common options:

```text
--max-bugs N             Stop once at least N new artifact bundles exist. A batch may exceed N. Default: 10.
--hours H                Stop after H wall-clock hours. Default: 4.
--max-empty-passes N     Stop after N hunter passes with no candidate. Default: 3.
--output-root DIR        Parent for cas-bug-results-* directories. Default: cwd.
--model MODEL            Override the Codex default model for all agents.
--no-dedup-search        Disable web search for the dedup agent.
--dry-run                Print/write planned Codex prompts without launching real agents.
--skip-git-repo-check    Pass through to codex exec for non-git test directories.
--writeup-report-name N  Filename for the standalone technical report under final-report/. Default: technical_report.tex.
--artifact-repo-url URL  Public repo URL where bug bundles are published; each bug card's Artifact field links to URL/tree/main/bug-report/<slug>. Default: empty (card shows the bundle path as plain text, no link).
--skip-pdf               Do not compile technical_report.tex to PDF after the write-up phase.
--latex-engine ENGINE    Engine for PDF compile: auto, an engine name, or a full path to a binary. Default: auto.
--sandbox MODE           Codex sandbox mode. Default: workspace-write.
--ask-for-approval MODE  Codex approval mode. Default: never.
--price-input USD        Override API-equivalent input-token price per 1M tokens.
--price-cached-input USD Override API-equivalent cached-input-token price per 1M tokens.
--price-output USD       Override API-equivalent output-token price per 1M tokens.
```

Token-cost reporting is an imputed API-equivalent estimate, not the amount billed
to a ChatGPT/Codex subscription. GPT-5.6 is a three-tier family (Sol, Terra, and
Luna). By default the harness uses OpenAI's July 2026 GPT-5.6 Sol (flagship) API
list rates: `$5.00`/1M input tokens, `$0.50`/1M cached input tokens, and
`$30.00`/1M output tokens. If `--model gpt-5.6-terra` (`$2.50`/`$0.25`/`$15.00`)
or `--model gpt-5.6-luna` (`$1.00`/`$0.10`/`$6.00`) is passed without explicit
`--price-*` overrides, the harness switches to the corresponding current
list-rate preset automatically.

## Safety

The runner defaults to:

```text
--sandbox workspace-write
--ask-for-approval never
```

Do not use `--sandbox danger-full-access` unless the entire run is inside a
disposable external sandbox such as a container or VM.
