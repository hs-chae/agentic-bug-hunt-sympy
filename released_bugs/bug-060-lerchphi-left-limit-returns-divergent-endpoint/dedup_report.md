---
verdict: family_known_specific_new
confidence: 84
---

## Candidate Summary

`limit(lerchphi(x, 1, 1), x, 1, dir="-")` returns `lerchphi(1, 1, 1)` instead of the divergent left-hand limit `oo`.

## Search Queries

- `SymPy limit lerchphi(x, 1, 1) x 1 oo`
- `site:github.com/sympy/sympy "lerchphi(x, 1, 1)"`
- `"limit(lerchphi(x, 1, 1)"`
- `gh issue list --search 'lerchphi limit'`
- `gh issue list --search 'lerchphi oo'`

## Closest Matches

- https://github.com/sympy/sympy/issues/8412 reports `Sum(1/x**2, (x, a, oo)).doit()` returning `lerchphi(1, 2, a)` and a later endpoint substitution producing `nan`; it asks for a `Piecewise` result.
- https://github.com/sympy/sympy/issues/14219 includes a finite sum containing `lerchphi(x, 1, k + 2)` with convergence conditions around `|x| <= 1` and `x != 1`, but is primarily about other summation failures.
- The Lerch transcendent series/convergence behavior is documented publicly, e.g. https://en.wikipedia.org/wiki/Lerch_transcendent and https://dlmf.nist.gov/25.14.

## Similarity Analysis

The broad LerchPhi/summation endpoint and convergence-condition family is public. The closest SymPy issues involve `lerchphi` appearing in sums and endpoint substitutions, not the direct limit of `lerchphi(x, 1, 1)` from the left.

## Specific Novelty Assessment

No public match found for `limit(lerchphi(x, 1, 1), x, 1, dir="-")` returning the unevaluated divergent endpoint. Existing reports would not automatically force Gruntz/limits to expand this special case to `-log(1 - x)/x` or return `oo`.

## Recommendation

continue_to_artifact_generation
