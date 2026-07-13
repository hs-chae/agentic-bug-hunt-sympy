---
verdict: duplicate
confidence: 90
---

## Correction (re-classification)

The original `novel` / "no public precedent" verdict is wrong. This is essentially the same as a long-standing **open** SymPy issue:

- https://github.com/sympy/sympy/issues/23836 — "Incorrect results for limits of Piecewise at discontinuity" (open, filed 2022-07-26). States explicitly that the value of the Piecewise at the boundary is irrelevant and should not be considered by `limit`. This is the identical root cause.
- https://github.com/sympy/sympy/issues/27236 — "bug with limit() function" (open, filed 2024-11-09). `Piecewise((1, x<0), (-1, x>=0))` one-sided limits return the wrong branch; the same mechanism and a sibling instance of this reproducer.

There are also open fix PRs targeting the exact function named here (`Piecewise._eval_as_leading_term` ignoring `cdir`):

- https://github.com/sympy/sympy/pull/29589 — "Fix Piecewise._eval_as_leading_term ignoring limit direction"
- https://github.com/sympy/sympy/pull/29538 — "Fix directional limits of Piecewise at discontinuities"
- https://github.com/sympy/sympy/pull/29920 — "limits: fix Piecewise leading term at a boundary condition"

The original searches below missed these because they queried the exact literal expression `Piecewise((0, x < 0), (1, True))` rather than the symptom (one-sided Piecewise limit at a discontinuity choosing the wrong branch) or the responsible function. The bug itself is real; only the novelty claim was incorrect.

---

## Candidate Summary

`limit(Piecewise((0, x < 0), (1, True)), x, 0, dir="-")` returns `1` in SymPy 1.14.0, even though values immediately to the left of `0` are on the `x < 0` branch and equal `0`.

## Search Queries

- `site:github.com/sympy/sympy Piecewise left hand limit x < 0 True branch limit dir='-' returns 1`
- `site:github.com/sympy/sympy "limit(Piecewise" "dir='-'" "x < 0"`
- `SymPy Piecewise left hand limit returns wrong branch`
- `"Piecewise((0, x < 0), (1, True))" SymPy`
- `"limit(Piecewise((0" "dir" "SymPy"`
- `"left-hand limit" "Piecewise" "SymPy"`

## Closest Matches

- SymPy's public limit tests include many one-sided limit checks, including issue-specific regressions for `dir="-"`, but I did not find a public test or issue for a discontinuous `Piecewise((0, x < 0), (1, True))` choosing the wrong side.
- SymPy's Piecewise tests cover branch simplification, intervals, integration, and substitution behavior, but not this exact one-sided limit at a jump with a default `True` branch.

## Similarity Analysis

The closest public material is subsystem-level: one-sided limits and Piecewise branch logic are both heavily tested. That does not establish a duplicate under the harness criterion. I found no public report saying that `limit` substitutes at the boundary before respecting `dir`, and no existing issue/PR whose described resolution would automatically fix this specific left-branch selection failure.

## Specific Novelty Assessment

The minimal reproducer is very small and exact searches for it did not find a public match. The broad family of Piecewise boundary handling is known, but this particular left-hand limit returning the default/right branch appears new.

## Recommendation

continue_to_artifact_generation
