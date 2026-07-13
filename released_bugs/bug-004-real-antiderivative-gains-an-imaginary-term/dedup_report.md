---
verdict: family_known_specific_new
confidence: 78
---

## Candidate Summary

`integrate(log(x)/(x**2 - 1), x)` returns an antiderivative whose derivative differs from the original integrand by an extra branch term. At `x = 2`, `diff(F, x) - log(x)/(x**2 - 1)` numerically gives `-I*pi/2` instead of `0`.

## Search Queries

- `site:github.com/sympy/sympy "log(x)/(x**2 - 1)"`
- `site:github.com/sympy/sympy "integrate(log(x)/(x**2-1)"`
- `"log(x)/(x**2 - 1)" "SymPy"`
- `"diff(integrate(log(x)/(x**2 - 1)"`
- `SymPy issue integrate log(x)/(x**2-1) imaginary pi branch`
- `SymPy polylog integral log(x)/(x^2 - 1) branch cut`
- `SymPy integrate log(x)/(x**2-1) wrong antiderivative`
- `"SymPy" "branch cut" "integrate" "polylog" "I*pi"`
- `"SymPy" "integrate" "polylog" "branch" "wrong"`

## Closest Matches

- Open issue sympy/sympy#13850 ("Integration result appears to use a different branch of polylog"), https://github.com/sympy/sympy/issues/13850 — `integrate(log(x)/(1+x), x)` returns a wrong antiderivative built from a shifted-log/polylog branch that does not differentiate back to `log(x)/(x+1)`. This is the same root-cause family: the present bug reduces by parts to exactly the `Integral(log(x±1)/x)` subintegrals (see `root_cause.md`), so #13850 is a direct, open, previously-missed match. The original "novel" claim resulted from searching only the literal string `log(x)/(x**2 - 1)`.
- Related branch-artifact integration issues: sympy/sympy#23337 (https://github.com/sympy/sympy/issues/23337, spurious `I*pi` in a definite integral) is the same broad family of branch-cut integration defects.
- SymPy integrals documentation: https://docs.sympy.org/latest/modules/integrals/integrals.html documents that `integrate(f, x)` returns an indefinite integral and gives examples with logarithmic rational functions.
- Broad public material exists for branch cuts in complex logarithms and polylogarithmic expressions; the focused literal-string searches did not surface the `log(x)/(x**2 - 1)` expression or the residual `-I*pi/2`, but the shifted-log/polylog branch family is publicly known via #13850.

## Similarity Analysis

This belongs to a known public family of integration branch-cut bugs in which an antiderivative built from a shifted-log/polylog branch differentiates back incorrectly on a real interval. Open issue sympy/sympy#13850 (https://github.com/sympy/sympy/issues/13850) reports this same family for `integrate(log(x)/(1+x))`. The specific case `log(x)/(x**2 - 1)` evaluated at `x = 2` with extra term `-I*pi/2`, and the parametrized `log(x)/(x**2 - a**2)` family, were not individually reported, so this is a new specific instance of that known family rather than an unreported failure mode.

The public SymPy documentation establishes the expected contract for indefinite integration but does not describe this failure mode or a repair that would necessarily cover it.

## Specific Novelty Assessment

The known family is captured by open issue sympy/sympy#13850 (https://github.com/sympy/sympy/issues/13850), which covers the shifted-log/polylog branch-cut antiderivative mechanism. The exact instance here — `log(x)/(x**2 - 1)` at `x = 2`, residual `-I*pi/2`, and the `log(x)/(x**2 - a**2)` family — is a new specific case not previously reported, so it remains individually actionable as a regression test even though the family is publicly known.

## Recommendation

continue_to_artifact_generation
