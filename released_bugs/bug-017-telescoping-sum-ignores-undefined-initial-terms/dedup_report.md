---
verdict: family_known_specific_new
confidence: 82
---

## Candidate Summary

`Sum(1/(k*(k - 1)), (k, 0, oo)).doit()` returns `-1` even though the terms at `k=0` and `k=1` are `zoo`; the well-defined tail from `k=2` sums to `1`.

## Search Queries

- `"Sum(1/(k*(k - 1)), (k, 0, oo))" SymPy`
- `"1/(k*(k - 1))" "Sum" "SymPy" "-1"`
- `site:github.com/sympy/sympy/issues telescoping sum singular terms Sum doit`
- `site:github.com/sympy/sympy/issues summation ignores poles undefined terms`
- `"1/(k*(k - 1))" "zoo" "SymPy"`

## Closest Matches

- https://docs.sympy.org/latest/modules/concrete.html documents Gosper/telescoping summation machinery, but does not report this invalid finite value.
- https://github.com/sympy/sympy/issues/8746 (open, "summation over poles of rational functions") reports the SAME failure mode: `summation(1/(k*(k+1)), (k, -3, n))` returns a finite closed form despite poles in the summation range. This is the known family for this bug.
- https://github.com/sympy/sympy/issues/12018 is a different summation limitation where a solution is not found.
- https://github.com/sympy/sympy/issues/5229 is an unrelated old limit/summation issue.

## Similarity Analysis

The general failure mode — partial-fraction/telescoping summation ignoring poles inside the range and returning a finite value — is already documented in open issue https://github.com/sympy/sympy/issues/8746. This specific instance (`Sum(1/(k*(k - 1)), (k, 0, oo)).doit()` returning -1 with `zoo` initial terms, plus the shifted family) is not separately reported.

## Specific Novelty Assessment

The bug family is known via issue #8746. This is a specific new instance within that known family: a closed-form telescoping result applied across poles at the start of an infinite summation range, with a concise reproducer and a directly protective regression test. It should be classed `family_known_specific_new`, citing https://github.com/sympy/sympy/issues/8746.

## Recommendation

continue_to_artifact_generation
