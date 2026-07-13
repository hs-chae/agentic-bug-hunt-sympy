---
verdict: family_known_specific_new
confidence: 80
---

## Candidate Summary

`solveset(Eq(acot(x), -pi/2), x, S.Reals)` returns `{0}` in SymPy 1.14.0. This returned point is not a solution because SymPy has `acot(0) = pi/2`, so the residual against `-pi/2` is `pi`.

## Search Queries

- `"solveset(Eq(acot(x), -pi/2)"`
- `"acot(x)" "-pi/2" "solveset"`
- `site:github.com/sympy/sympy/issues "acot" "-pi/2"`
- `site:github.com/sympy/sympy/issues "acot(0)" "pi/2"`
- `SymPy issue inverse trigonometric solveset acot branch`
- `Stack Overflow SymPy acot solveset -pi/2`

## Closest Matches

- SymPy `solveset` documentation states that returned sets are values for which the equation is true: https://docs.sympy.org/latest/modules/solvers/solveset.html#sympy.solvers.solveset.solveset
- SymPy issue #17334 is a broad public discussion of trigonometric solving and inversion limitations in `solveset`: https://github.com/sympy/sympy/issues/17334
- General inverse-trigonometric references document that inverse trig functions are branch/range-sensitive: https://en.wikipedia.org/wiki/Inverse_trigonometric_functions
- No public report was found for `acot(x) = -pi/2`, for `solveset` returning `{0}`, or for this exact `acot(0)` residual failure.

## Similarity Analysis

The candidate belongs to a known family of inverse-function branch/range mistakes: applying a direct trigonometric inverse step can generate a value that does not satisfy the original principal inverse-trig equation. Public SymPy issue #17334 covers trigonometric inversion machinery in `solveset`, but it does not mention `acot`, the endpoint `-pi/2`, or the false solution `{0}`.

Existing local artifacts in this workspace include related inverse-trig cases, but those are not public prior art. The public record found during search is family-level only.

## Specific Novelty Assessment

The broad inverse-trig branch-validation family is known, while this exact real-domain `acot` endpoint reproducer appears publicly new. A comprehensive branch-checking fix could cover it, but no located public issue or PR clearly requires this case.

## Recommendation

continue_to_artifact_generation
