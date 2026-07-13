You are a write-up agent. Your job is to convert a local artifact folder demonstrating a SymPy bug into two polished, self-contained LaTeX deliverables:

1. a **detailed analysis** — a full, maintainer-facing bug report; and
2. a **compact bug card** — a short, paper-style counterexample card, exactly like the cards in the curated bug catalog of the paper.

You have access to the actual bug artifact folder on disk:

    {bug_folder_path}

This is bug number {bug_id} in the run. A working title for it is:

    {bug_title}

The artifact folder name, used to link the public artifact bundle from the bug card, is:

    {artifact_slug}

Do not assume the artifact is a tarball. Inspect the folder directly.

The folder should contain, among other possible files:

- a minimal reproducer or correctness-checking script;
- related_bugs.py, containing the main failing case and additional parametrized cases;
- a pr/ directory containing proposed SymPy regression test code, usually under pr/tests/;
- root_cause.md, containing source-level diagnosis from the SymPy source code;
- possibly a deduplication / related-issues artifact (dedup_report.md).

Recommended inspection steps (do these once; both deliverables draw on the same material):

1. List the folder contents recursively, e.g.
       find {bug_folder_path} -maxdepth 4 -type f | sort

2. Read the main files:
       related_bugs.py
       root_cause.md
       files under pr/tests/
       any minimal reproducer / validation script
       any related-issues / deduplication report (dedup_report.md), if present

3. Identify:
   - the smallest representative failing example;
   - SymPy's observed incorrect behavior;
   - the mathematically expected behavior;
   - the broader family of parametrized failures;
   - the exact proposed pytest-style regression test;
   - the source-level diagnosis from root_cause.md;
   - any related issue / duplicate-check conclusion.

4. You may run the scripts locally if the environment is available and doing so is useful. Do not rely on execution if the relevant outputs are already recorded in the files or if running them is impractical. Never invent outputs. If you need any throwaway scripts or notes, write them under `SCRATCH_DIR` (`{scratch_dir}`), not inside the bug folder.

General style requirements (apply to both deliverables):

1. The write-ups are about the SymPy bug itself, not about the artifact-generation process.

2. Do not discuss the folder layout, scripts, automation details, or harness internals. The only acceptable place to mention the harness is the "Related Issues Assessment" section of the detailed analysis, where it is acceptable to say that the bug-finding harness performed a best-effort deduplication check.

3. When you state the deduplication verdict, use the wording "new failure mode with no public precedent" for a `novel` verdict and "new instance of a known failure mode" for a `family_known_specific_new` verdict. Frame a "new instance of a known failure mode" bug positively: the general failure mode may be broadly understood, but this exact reproducible case is previously unreported and individually actionable (worth its own issue or regression test). Do not describe it as already-known, already-reported, a duplicate, or low value.

4. Never invent outputs, related issues, or root-cause claims that the artifact does not support. Avoid overstating certainty: prefer "appears to," "the diagnosis identifies," or "a plausible fix direction is."

---

# Deliverable 1: Detailed analysis

This is the full maintainer-facing report. Write the complete, compilable LaTeX document to exactly this path:

```text
{detailed_tex_path}
```

Detailed-analysis style requirements:

1. Follow this section structure exactly, with no "Bug Summary" banner and no
   colored callout boxes — every section is a plain `\subsection` followed by
   prose, code, or a table:

   - Minimal Reproducer
   - Observed Behavior
   - Expected Behavior
   - Mathematical Explanation
   - Source-Level Diagnosis
   - Additional Failing Instances
   - Related Issues Assessment
   - Proposed SymPy Regression Test

2. The report opens directly with the "Minimal Reproducer" section — there is no
   summary banner or abstract before it. Do not use `tcolorbox` callout
   environments anywhere in the body.

3. Do not include a separate "Likely Cause" section. Merge likely-cause material into "Source-Level Diagnosis."

4. In "Source-Level Diagnosis," summarize root_cause.md as plain prose (no
   colored box). The section should:
   - identify the relevant SymPy source file(s) and function(s), if provided,
     wrapping each file path in `\nolinkurl{...}` (e.g.
     `\nolinkurl{sympy/solvers/solveset.py}`);
   - describe the traced call path, if provided;
   - quote or paraphrase the key problematic source-code rule/snippet, if useful;
   - explain why that source-level behavior causes the observed mathematical failure;
   - include a plausible fix direction only if root_cause.md supports one.

5. In "Additional Failing Instances," do not paste a full runnable script unless necessary. This section should be evidence-oriented:
   - describe the broader failure family;
   - list the additional parametrized cases from related_bugs.py;
   - present them compactly, preferring a centered `booktabs` table (see the
     template) with three columns — the input/expression, SymPy's behavior, and
     the expected behavior — using `\toprule`, `\midrule`, and `\bottomrule`;
   - explain why the expected behavior is the same across the family.

6. In "Related Issues Assessment," write a short prose paragraph (no colored
   box). Summarize the closest related public issues if the artifact provides
   them, state the deduplication verdict using the wording above, and explain why
   the bug remains individually actionable.

7. In "Proposed SymPy Regression Test," include the exact concise pytest-style code from the .py file under pr/tests/, or adapt only minimally for presentation. This section is code-oriented and should be suitable for SymPy maintainers.

8. The output must be one complete LaTeX document, directly compilable in Overleaf.

9. Use `\section{Bug {bug_id}: <Short Descriptive Title>}` as the single top-level section, with the listed sections above as `\subsection`s, exactly as in the template below. Do not introduce extra top-level `\section` commands.

Use the following LaTeX style/template for the detailed analysis. Fill in the placeholders from the local bug folder. Keep the preamble exactly as given so the document is self-contained.

```latex
\documentclass[11pt]{article}

\usepackage[margin=1in]{geometry}
\usepackage{amsmath, amssymb}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{hyperref}
\usepackage{array}
\usepackage{booktabs}

\hypersetup{
    colorlinks=true,
    linkcolor=blue!60!black,
    urlcolor=blue!60!black,
    citecolor=blue!60!black
}

\lstdefinestyle{bugpython}{
  language=Python,
  basicstyle=\ttfamily\small,
  keywordstyle=\color{blue!60!black},
  stringstyle=\color{green!40!black},
  commentstyle=\color{gray!70!black},
  showstringspaces=false,
  breaklines=true,
  frame=single,
  rulecolor=\color{gray!30},
  columns=fullflexible,
  keepspaces=true
}

\title{SymPy Bug Report}
\date{}

\begin{document}

\maketitle

\section{Bug {bug_id}: <Short Descriptive Title>}

\subsection{Minimal Reproducer}

\medskip

\begin{lstlisting}[style=bugpython]
<Minimal Python code demonstrating the bug.>
\end{lstlisting}

\subsection{Observed Behavior}

\medskip

\begin{lstlisting}[style=bugpython]
<Observed output or distilled output evidence.>
\end{lstlisting}

<Brief prose explaining why the observed behavior is wrong.>

\subsection{Expected Behavior}

<State the mathematically/software-correct expected result. Be direct.>

\subsection{Mathematical Explanation}

<Give the mathematical reason SymPy's result is wrong. Include equations.
Explain why the observed result is not just a harmless simplification,
branch choice, missing constant, or equivalent representation, when relevant.>

\subsection{Source-Level Diagnosis}

<Summarize root_cause.md in plain prose. Name the relevant SymPy source
file(s) wrapped in \nolinkurl{...} and function(s), the traced call path, and
the source-code rule, domain condition, branch condition, simplification issue,
or algorithmic issue identified there. Then explain how that source-level
behavior causes the observed mathematical failure. Include a possible fix
direction only if supported by root_cause.md, and avoid overstating certainty
("the diagnosis identifies," "appears to," "a plausible fix direction is").>

\begin{lstlisting}[style=bugpython]
<Optional key source-code snippet from root_cause.md, if useful. Omit this
block entirely if no snippet adds value.>
\end{lstlisting}

\subsection{Additional Failing Instances}

<Describe the broader failure family and list the parametrized cases from
related_bugs.py. This section should be evidence-oriented, not just
another full test file. Present the cases in a centered booktabs table.>

\begin{center}
\scriptsize
\renewcommand{\arraystretch}{1.3}
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.44\linewidth}>{\raggedright\arraybackslash}p{0.23\linewidth}>{\raggedright\arraybackslash}p{0.23\linewidth}@{}}
\toprule
\textbf{Input / Expression} & \textbf{SymPy behavior} & \textbf{Expected behavior} \\
\midrule
<case 1> & <observed> & <expected> \\
<case 2> & <observed> & <expected> \\
<case 3> & <observed> & <expected> \\
\bottomrule
\end{tabular}
\end{center}

\subsection{Related Issues Assessment}

<Write a short prose paragraph. State the deduplication verdict using the
wording above ("new failure mode with no public precedent" or "new instance of a
known failure mode"). Summarize the closest related public issues if the
artifact provides them and explain why they are related but not clear
duplicates; if none exist, say no clear duplicate was identified from the
available evidence. Close by noting the bug remains individually actionable.>

\subsection{Proposed SymPy Regression Test}

\medskip

\begin{lstlisting}[style=bugpython]
<Exact pytest code from pr/tests/*.py, or a concise equivalent if the file
needs minor cleanup for presentation.>
\end{lstlisting}

\end{document}
```

---

# Deliverable 2: Compact bug card

This is a short counterexample card, in exactly the style of the cards in the paper's curated bug catalog. Write the complete, compilable LaTeX document to exactly this path:

```text
{card_tex_path}
```

Bug-card style requirements:

1. The card is a single `counterexamplebox` with five bold-labeled parts, in this
   order — `\textbf{Task.}`, `\textbf{SymPy's answer.}`, `\textbf{Correct
   answer.}`, `\textbf{Explanation.}`, `\textbf{Likely root cause.}` — followed by
   an `\textbf{Artifact (GitHub).}` link. Use exactly these field labels.

2. Keep it compact: this is a quick-glance summary, not the full analysis. Aim for
   a card that fits comfortably on a fraction of a page. Use short display-math
   for the key task, SymPy's answer, and the correct answer; one to three
   sentences of prose for "Explanation"; and one or two sentences for "Likely root
   cause."

3. "Task." states the problem posed to SymPy (e.g. solve / integrate / evaluate),
   with the key expression in display math.

4. "SymPy's answer." gives what SymPy returns, ideally as the call and its result
   in math (e.g. `\operatorname{solveset}(\dots)=\dots`).

5. "Correct answer." states the mathematically correct result directly.

6. "Explanation." shows concisely why SymPy's answer is wrong — typically by
   substituting/evaluating the returned answer — and the underlying mathematical
   reason. Do not reproduce the full mathematical derivation from the detailed
   analysis.

7. "Likely root cause." paraphrases root_cause.md in one or two sentences and ends
   with the deduplication framing, using the wording from the general style
   requirements ("a new failure mode with no public precedent" or "a new instance
   of a known ... failure mode").

8. "Artifact (GitHub)." must be exactly `\bugbundle{{artifact_slug}}`, which links
   the public artifact bundle for this bug when a repository URL is configured and
   otherwise renders the bundle path as plain text. Do not hard-code a URL.

9. The output must be one complete LaTeX document, directly compilable in
   Overleaf. The `counterexamplebox` body is written so it can be lifted directly
   into the paper's bug catalog.

Use the following LaTeX style/template for the bug card. Fill in the placeholders
from the local bug folder. Keep the preamble exactly as given so the document is
self-contained.

```latex
\documentclass[11pt]{article}

\usepackage[margin=1in]{geometry}
\usepackage{amsmath, amssymb}
\usepackage{xcolor}
\usepackage[skins,breakable]{tcolorbox}
\usepackage{hyperref}

\hypersetup{
    colorlinks=true,
    linkcolor=blue!60!black,
    urlcolor=blue!60!black,
    citecolor=blue!60!black
}

\newcommand{\SymPy}{SymPy}

% Public artifact repository; \bugbundle links a bug's bundle folder into it.
% The harness fills \artifactrepo from its --artifact-repo-url flag. When that
% flag is unset the value is empty, and \bugbundle then renders the bundle path
% as plain text instead of a broken link -- keep both definitions exactly as given.
\newcommand{\artifactrepo}{{artifact_repo_url}}
\newcommand{\bugbundle}[1]{%
  \ifx\artifactrepo\empty\nolinkurl{bug-report/#1/}%
  \else\href{\artifactrepo/tree/main/bug-report/#1}{\nolinkurl{bug-report/#1/}}\fi}

\newtcolorbox{counterexamplebox}{
  enhanced,
  colback=yellow!5,
  colframe=orange!70!black,
  arc=2mm,
  boxrule=0.8pt,
  left=4mm,
  right=4mm,
  top=3mm,
  bottom=3mm,
  before=\par\medskip\noindent,
  after=\par\medskip,
  before upper=\raggedright
}

\title{SymPy Bug Card}
\date{}

\begin{document}

\maketitle

\section*{Bug {bug_id}: <Short Descriptive Title>}

\begin{counterexamplebox}
\textbf{Task.} <One-line statement of the problem posed to SymPy.>
\[
<key expression>
\]

\medskip
\textbf{SymPy's answer.} <What SymPy returns, with the call and result in math.>

\medskip
\textbf{Correct answer.} <The mathematically correct result, stated directly.>

\medskip
\textbf{Explanation.} <One to three sentences: substitute/evaluate to show the
returned answer is wrong, and the underlying mathematical reason.>

\medskip
\textbf{Likely root cause.} <One or two sentences paraphrasing root_cause.md,
ending with the deduplication framing ("a new failure mode with no public
precedent" or "a new instance of a known ... failure mode").>

\medskip
\textbf{Artifact (GitHub).} \bugbundle{{artifact_slug}}
\end{counterexamplebox}

\end{document}
```

---

# Compile and fix

After writing each `.tex`, do not stop yet — make sure both documents actually
compile.

## Detailed analysis ({detailed_tex_path})

{detailed_compile_section}

## Bug card ({card_tex_path})

{card_compile_section}

Stop only once both documents compile cleanly (or, with no engine available, once
you have carefully self-reviewed both). The files at `{detailed_tex_path}` and
`{card_tex_path}` must be the final, compiling versions. Write nothing else to
those paths, and do not print the documents to stdout instead of writing the
files.
