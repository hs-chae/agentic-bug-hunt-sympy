---
verdict: family_known_specific_new
confidence: 76
---

## Candidate Summary

`integrate(1/(x*sqrt(x**2 - 1)), x)` returns an antiderivative whose derivative has the opposite real sign at `x = -3`. The returned expression differentiates correctly on the positive real branch but not on the negative real branch.

## Search Queries

- `SymPy integrate 1/(x*sqrt(x**2-1)) wrong sign negative x`
- `site:github.com/sympy/sympy "1/(x*sqrt(x**2 - 1))"`
- `"1/(x*sqrt(x**2-1))" "SymPy"`
- `"acosh(1/x)" "asin(1/x)" "SymPy" integrate`
- `SymPy issue branch cut integration sqrt(x**2 - 1)`
- `SymPy issue integrate returns wrong sign negative real branch sqrt`

## Closest Matches

- SymPy's public tests include nearby branch-sensitive expressions involving `sqrt(x**2 - 1)`, inverse trig/hyperbolic rewrites, and a positive-interval definite integral `integrate(1/(x*sqrt(x**2 - 1)), (x, 1, 2)) == pi/3`.
- Known-family public issues (same `sqrt(x**2 - 1)` integration family, same negative-real sign-loss / meijerg `acosh`/`asin` branch machinery):
  - sympy/sympy#20982 (CLOSED), "integrate(1 / (x ** 2 * sqrt(x ** 2 - 1))) gives wrong integral (lost sign when x < 0)" — same negative-real sign-loss symptom on a sibling `1/(x**n*sqrt(x**2-1))` integrand: https://github.com/sympy/sympy/issues/20982
  - sympy/sympy#23566 (OPEN), "integrate(1/sqrt(x**2-1)) shouldn't be acosh(x)" — same Meijer-G `Piecewise(acosh, asin)` branch handling for `sqrt(x**2-1)`: https://github.com/sympy/sympy/issues/23566
- These are the public known-family precedents. No public issue/PR targets the exact `1/(x*sqrt(x**2 - 1))` indefinite integral having the wrong sign on negative real inputs, so the specific counterexample remains new.

## Similarity Analysis

This is in a known risky family: inverse trig/hyperbolic rewrites and square-root branch handling. The nearest public material exercises the positive branch or related functions, not the negative-real derivative check. Resolving the positive-interval tests or generic branch-cut discussions would not automatically fix this exact negative-branch sign error.

## Specific Novelty Assessment

The broad branch-cut subsystem is known, but the minimized expression and concrete negative-real counterexample appear specific and new after focused searching.

## Recommendation

continue_to_artifact_generation
