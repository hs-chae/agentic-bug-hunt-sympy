---
verdict: family_known_specific_new
confidence: 80
---

## Candidate Summary

`solve_univariate_inequality(x**(S(1)/3) <= 1, x, relational=False)` returns `Interval(-oo, 1)`, including negative real inputs where SymPy's principal `x**(1/3)` is complex and the real inequality is not satisfied.

## Search Queries

- `"SymPy solve_univariate_inequality x**(1/3) <= 1 negative real principal branch"`
- `site:github.com/sympy/sympy solve_univariate_inequality fractional powers real domain`
- `site:github.com/sympy/sympy "solve_univariate_inequality" "x**(1/3)"`
- `"SymPy inequality fractional power principal branch negative real bug"`

## Closest Matches

- SymPy's root documentation says `root(x, n)` defaults to the principal root and gives `root(x, 3) -> x**(1/3)`: https://docs.sympy.org/latest/modules/functions/elementary.html#sympy.functions.elementary.miscellaneous.root
- The same page distinguishes `real_root` from principal roots for negative arguments.
- SymPy's inequality tests include many public issue regressions, but local inspection did not find the exact fractional-power inequality.

## Similarity Analysis

The public documentation establishes that negative real values are not automatically in the real-valued domain of `x**(1/3)`. That makes the returned interval suspicious, but the public material is semantic documentation rather than a bug report for `solve_univariate_inequality`.

## Specific Novelty Assessment

Focused searches did not find an existing public report of this inequality or the exact wrong interval `Interval(-oo, 1)`. The broad family of principal-root/domain filtering problems is known, but resolving a documented root-semantics note or unrelated inequality issue would not automatically resolve this candidate.

## Recommendation

continue_to_artifact_generation
