---
verdict: novel
confidence: 84
---

## Candidate Summary

Candidate 2 is a solver domain bug. In SymPy 1.14.0, `nonlinsolve([(x*y - x)/(x - 1) - y, y - 1], [x, y])` returns `{(1, 1)}` even though substituting `(1, 1)` into the original rational equation gives `nan` because the denominator `x - 1` is zero. The expected result is `EmptySet`.

## Search Queries

- `site:github.com/sympy/sympy nonlinsolve rational denominator returns solution undefined`
- `site:github.com/sympy/sympy "nonlinsolve" "denominator" "x - 1"`
- `site:github.com/sympy/sympy "nonlinsolve" "nan" "denominator"`
- `"nonlinsolve([(x*y - x)/(x - 1) - y, y - 1]"`
- `SymPy nonlinsolve extraneous solution denominator rational equation issue`
- `SymPy nonlinsolve returns solution denominator zero`
- `SymPy solveset nonlinsolve _simple_dens denominator exclude bug`
- `"nonlinsolve" "x - 1" "denominator"`
- `"nonlinsolve result = {(1, 1)}"`
- `"nonlinsolve" "residuals = [nan, 0]"`
- `" _simple_dens" "nonlinsolve"`
- `Stack Overflow SymPy nonlinsolve denominator zero`
- `Google Groups sympy nonlinsolve denominator`

## Closest Matches

- Public SymPy source on GitHub, `sympy/solvers/solveset.py`, shows `nonlinsolve` still has an early return when `not remaining`, before the later `substitution(..., exclude=denominators)` path: https://raw.githubusercontent.com/sympy/sympy/master/sympy/solvers/solveset.py
- General mathematical background on extraneous roots from clearing rational denominators exists, for example Wikipedia's "Extraneous and missing solutions": https://en.wikipedia.org/wiki/Extraneous_and_missing_solutions
- Focused searches did not find a public SymPy issue, PR, Stack Overflow post, mailing-list discussion, or release note containing this exact `nonlinsolve` system, the returned `{(1, 1)}`, the residual `[nan, 0]`, or the suspected `_simple_dens`/`exclude=denominators` bypass.

## Similarity Analysis

The broad bug family is well known mathematically: clearing denominators can introduce extraneous solutions at denominator zeros. That general family does not make this a duplicate. The candidate is about a specific `nonlinsolve` control-flow path where denominator exclusions are recorded but bypassed when the polynomial subsystem solves everything.

The current public source is useful context because it shows the same denominator-aware machinery and the same early-return structure, but it is not itself a public bug report. I found no public issue or PR whose resolution would necessarily filter zero-dimensional `nonlinsolve` polynomial solutions against the recorded denominators.

## Specific Novelty Assessment

The exact minimal system appears new in public reports found by focused searching. No close public match describes `[(x*y - x)/(x - 1) - y, y - 1]`, the invalid result `{(1, 1)}`, or the bypass of `exclude=denominators` in the no-remaining-equations branch. Similar reports about rational-equation extraneous roots would need to specifically cover `nonlinsolve` denominator filtering to satisfy the duplicate criterion, and I did not find one.

## Recommendation

continue_to_artifact_generation
