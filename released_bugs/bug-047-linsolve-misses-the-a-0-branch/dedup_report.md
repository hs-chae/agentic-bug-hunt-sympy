---
verdict: family_known_specific_new
confidence: 70
---

## Candidate Summary

`linsolve([a*x - a], [x])` returns `{(1,)}` in SymPy 1.14.0. The equation is `a*(x - 1) = 0`; when `a = 0`, every `x` satisfies the equation, so the returned generic solution misses the `a = 0` branch.

## Search Queries

- `"linsolve([a*x - a], [x])"`
- `"a*x - a" "linsolve" "SymPy"`
- `site:github.com/sympy/sympy/issues "linsolve" "symbolic coefficients" "parameters"`
- `site:github.com/sympy/sympy/issues "linsolve" "a*x - a"`
- `SymPy linsolve symbolic parameter zero branch`
- `SymPy linsolve symbolic coefficients determinant singular parameters issue`

## Closest Matches

- SymPy's `linsolve` documentation includes a "Solve for symbolic coefficients" example returning formulas with denominator `a*e - b*d`, without showing singular-parameter case splits: https://docs.sympy.org/latest/modules/solvers/solveset.html#sympy.solvers.solveset.linsolve
- The solveset documentation notes more generally that symbolic parameters are not handled well for all cases: https://docs.sympy.org/latest/modules/solvers/solveset.html
- Open issue sympy/sympy#16861, "Proper solution of linear equations with symbolic coefficients" (open, 18 comments, created 2019-05-20): https://github.com/sympy/sympy/issues/16861 — documents this exact symbolic-coefficient missing-`a = 0`-branch problem. It gives the essentially identical example `a*x = b` (the bug's `a*x - a` is the `b = a` case), notes that solve/solveset/linsolve solutions "are not valid for a=0", and proposes a `linsolve_cond([a*x-b],[x])` that returns the conditional `a = 0` branch.

## Similarity Analysis

The documentation is close at the behavior-family level because it shows `linsolve` producing generic symbolic-coefficient formulas with determinant denominators rather than explicit singular branches. Issue #16861 is the directly on-point public report: it raises the same symbolic-coefficient missing-`a = 0`-branch problem for `a*x = b` and asks that linsolve carry the conditional degenerate branch. This bug's `linsolve([a*x - a], [x])` is the `b = a` special case of that issue.

This behavior is also linsolve's long-standing documented generic-coefficient convention (the docstring's own symbolic-coefficient example returns a determinant-denominator formula and never splits singular-parameter branches), and it is unchanged across 1.12, 1.14.0, and dev-master — i.e. a known, long-standing limitation rather than a fresh regression.

## Specific Novelty Assessment

The broad family is known and the specific missing-`a = 0`-branch failure mode is publicly documented in open issue #16861 for `a*x = b`. The exact minimal reproducer `linsolve([a*x - a], [x])` (the `b = a` case) and its specific `{(1,)}` result are not separately reported, but they fall squarely within the failure mode #16861 describes; they are an individually actionable instance, not a novel failure mode.

## Recommendation

continue_to_artifact_generation
