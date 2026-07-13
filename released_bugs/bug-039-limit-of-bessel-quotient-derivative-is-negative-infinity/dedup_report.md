---
verdict: novel
confidence: 86
---

## Candidate Summary

`limit(diff(besselj(1, x)/x, x), x, 0)` returns `-oo`, but `besselj(1, x)/x = 1/2 - x**2/16 + O(x**4)`, so its derivative tends to `0`.

Suspected cause: the limit/leading-term machinery misses cancellation between differentiated Bessel recurrence terms and reports a spurious negative-power term.

## Search Queries

- `SymPy limit diff(besselj(1,x)/x,x) x 0 -oo`
- `"besselj(1, x)/x" "limit" "SymPy"`
- `site:github.com/sympy/sympy/issues "besselj(1, x)/x"`
- `"limit(diff(besselj" "SymPy"`
- `"besselj" "gruntz" "-oo" "SymPy"`
- `"besselj" "mrv_leadterm" "SymPy"`
- `"besselj(0, x)/2 - besselj(2, x)/2"`
- `"limit" "besselj" "SymPy" "wrong"`

## Closest Matches

- [SymPy limits documentation](https://docs.sympy.org/latest/modules/series/series.html) describes the `limit` function and notes that the Gruntz algorithm is used after heuristics. This is subsystem background, not a public bug report.
- [SymPy Gruntz source documentation mirror](https://www.aidoczh.com/sympy/_modules/sympy/series/gruntz.html) includes comments and implementation context for special-function limits and leading terms. It does not mention this Bessel quotient.
- [SymPy Bessel source documentation mirror](https://www.aidoczh.com/sympy/_modules/sympy/functions/special/bessel.html) documents Bessel functions and their Laurent behavior, but not this limit failure.

## Similarity Analysis

The closest materials are documentation/source mirrors for the relevant machinery. They help locate the likely subsystem but are not duplicate reports. Searches for the exact expression, exact wrong output `-oo`, and the differentiated recurrence expression did not surface a public issue or discussion.

## Specific Novelty Assessment

No public report was found for the exact Bessel reproducer or for a public issue whose fix would necessarily make the cancellation in `diff(besselj(1, x)/x, x)` visible to `limit`. Similarity is limited to the general fact that Gruntz and special-function leading terms are involved.

## Recommendation

continue_to_artifact_generation
