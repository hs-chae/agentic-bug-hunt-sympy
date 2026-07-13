---
verdict: family_known_specific_new
confidence: 82
---

## Candidate Summary

`limit(elliptic_k(x), x, 1, dir="-")` returns `zoo`, but along the real left side the complete elliptic integral `K(m)` diverges through positive real values, so the directional limit should be `oo`.

## Search Queries

- `SymPy elliptic_k limit 1 from left zoo oo`
- `"limit(elliptic_k" "1" "zoo" SymPy`
- `site:github.com/sympy/sympy/issues "elliptic_k" "zoo" "limit"`
- `site:github.com/sympy/sympy/issues "elliptic_k(x)" "dir"`
- `SymPy elliptic_k limit 1 zoo`

## Closest Matches

- https://github.com/sympy/sympy/issues/27058 reports a wrong `elliptic_k` limit on the branch cut for `limit(elliptic_k(2 + I*x), x, 0, "+/-")`; it is open and in the same limits/series family.
- https://github.com/sympy/sympy/issues/26250 reports an incorrect composite elliptic limit involving both `elliptic_e` and `elliptic_k`.
- https://github.com/sympy/sympy/pull/26264 fixed a hypergeometric nseries issue for nontrivial arguments and added a composite elliptic limit regression test.
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.ellipk.html documents the real integral definition and notes special handling near `m = 1`, but is not a SymPy bug report.

## Similarity Analysis

Issue #27058 is the closest function-level match, but it concerns approaching a point on the branch cut at parameter `2` from imaginary directions. Candidate 058 concerns the singular endpoint `m = 1` approached from the real left side, where the sign is determined as positive infinity.

Issue #26250/#26264 is also a related elliptic/hypergeometric limit family, but it was resolved by a PR already present historically while this candidate still reproduces. Neither public issue describes `limit(elliptic_k(x), x, 1, dir="-") -> zoo`.

## Specific Novelty Assessment

The broad elliptic-integral limit/nseries family is known. The exact directional endpoint-sign loss for `elliptic_k(x)` at `1-` appears specific and new. No public match was found whose resolution would automatically cover this reproducer.

## Recommendation

continue_to_artifact_generation
