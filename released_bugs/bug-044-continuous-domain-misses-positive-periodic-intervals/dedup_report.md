---
verdict: family_known_specific_new
confidence: 86
---

## Candidate Summary

`continuous_domain(sqrt(sin(x)), x, S.Reals)` returns only `Interval(0, pi)`. The real domain should include every interval where `sin(x) >= 0`, including points such as `5*pi/2`.

## Search Queries

- `site:github.com/sympy/sympy continuous_domain sqrt(sin(x)) Interval(0, pi)`
- `site:github.com/sympy/sympy continuous_domain sqrt(sin(x)) periodic`
- `"continuous_domain(sqrt(sin(x))"`
- `"sqrt(sin(x))" "continuous_domain"`
- `github sympy continuous_domain periodic inequalities trigonometric bug`
- `"solve_univariate_inequality" "periodic" "sympy" "issue"`
- `"solveset" "sin(x) >= 0" "Interval(0, pi)"`

## Closest Matches

The underlying root cause — a periodic inequality solved on a single fundamental period and returned as the full real solution, without lifting it over all integer translates — is a known, publicly reported defect. The original searches below missed it:

- https://github.com/sympy/sympy/issues/27573 — "`solveset(sin(x) > 0, x)` doesn't return all possible results" (OPEN). Reports `solveset(sin(x) > 0, x, S.Reals)` returning `Interval.open(0, pi)` instead of the periodic result — the exact single-period mechanism that feeds this `continuous_domain` symptom.
- https://github.com/sympy/sympy/issues/9721 — "solve_univariate_inequality returns wrong result for trigonometric inequalities" (CLOSED). Same family, same `solve_univariate_inequality` function.
- https://github.com/sympy/sympy/pull/27720 — "Fix periodic inequalities in solveset by lifting one-period solution" (CLOSED). Proposed fix for exactly this lifting defect (Fixes #27573).
- https://github.com/sympy/sympy/pull/27745 — "Fix `solve_univariate_inequality` for periodic solutions" (CLOSED). Proposed fix for the same periodic branch (Fixes #27573).

No public report was found for the exact reproducer `continuous_domain(sqrt(sin(x)), x, S.Reals)`, so the specific `continuous_domain` + `sqrt` radical-domain composition (and the missed `5*pi/2` witness) appears unreported. Search result pages also checked included:

- https://github.com/sympy/sympy/issues?q=is%3Aissue%20continuous_domain%20periodic
- https://github.com/sympy/sympy/issues?q=is%3Aissue%20sqrt(sin(x))

## Similarity Analysis

The root cause is in the broad family of periodic inequality solving: `solve_univariate_inequality(sin(x) >= 0, x)` solves on one period and does not lift the result back to all real periods. However, the focused searches did not find a public issue or PR that names this `continuous_domain` failure, the `sqrt(sin(x))` radical-domain composition, or the exact missing `5*pi/2` witness.

Generic discussions of periodic functions or square-root domains would not automatically resolve this candidate unless they specifically changed periodic inequality results used by `continuous_domain`.

## Specific Novelty Assessment

The root-cause defect is known, not novel: the periodic-inequality-solved-on-one-period mechanism is documented in OPEN issue #27573, closed issue #9721, and proposed fixes #27720 / #27745. What appears specific and new is the exact composition — `continuous_domain` over a radical `sqrt(sin(x))` whose `sin(x) >= 0` constraint inherits the un-lifted single-period result, with the missed `5*pi/2` witness. No public report describes this exact `continuous_domain` reproducer, so the case is family_known_specific_new: known family, individually new and actionable reproducer.

## Recommendation

continue_to_artifact_generation
