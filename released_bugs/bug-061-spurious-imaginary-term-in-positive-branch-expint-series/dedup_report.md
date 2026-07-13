---
verdict: family_known_specific_new
confidence: 76
---

## Candidate Summary

For positive `x`, `series(expint(2, x), x, 0, 2)` returns `1 + x*(log(x) - 1 + EulerGamma - I*pi) + O(x**2)`. The `-I*pi*x` term is spurious on the positive real branch.

## Search Queries

- `"series(expint(2, x), x, 0" SymPy`
- `"series(expint(2" "I*pi" SymPy`
- `"expint(2, x)" "EulerGamma - I*pi"`
- `site:github.com/sympy/sympy "series(expint(2" "I*pi"`
- GitHub issue search: `repo:sympy/sympy "series(expint(2"`
- GitHub issue search: `repo:sympy/sympy "expint(2, x)" "I*pi"`

## Closest Matches

- https://github.com/sympy/sympy/issues/6725 reports wrong order and coefficients for `expint(S(3)/2, -x).series(...)`. It is an `expint` series correctness issue, but with fractional order and a negative argument, not the positive-real `expint(2, x)` branch term.
- https://github.com/sympy/sympy/pull/26892 is an open PR adding `expint` series/leading-term support. The visible tests cover asymptotic series at infinity and limits like `limit(expint(3, x), x, oo)`, not the small-positive expansion at zero.
- https://github.com/sympy/sympy/issues/8712 discusses `expint(1, t*exp_polar(I*pi))`, polar lifting, and branch choices for negative real arguments.

## Similarity Analysis

The broad family is public: `expint` series and `expint`/polar branch behavior have known issues. However, I did not find a public issue, PR comment, or Stack Overflow report describing the exact small-`x` expansion of `expint(2, x)` with a false `-I*pi*x` term for a positive symbol.

PR #26892 changes nearby methods, but its public scope is leading/asymptotic behavior rather than the origin expansion that introduces this candidate's branch constant. Issue #6725 is also an `expint` series bug, but it is a different order, argument, and symptom.

## Specific Novelty Assessment

No public match was found whose resolution would necessarily remove the `-I*pi*x` term from `series(expint(2, x), x, 0, 2)` for positive real `x`. This appears to be a specific new manifestation of the known `expint` branch/series family.

## Recommendation

continue_to_artifact_generation
