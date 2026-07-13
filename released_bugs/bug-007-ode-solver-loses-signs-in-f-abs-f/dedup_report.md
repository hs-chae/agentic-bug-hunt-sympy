---
verdict: family_known_specific_new
confidence: 73
---

## Candidate Summary

`dsolve(Eq(f'(x), sqrt(f(x)**2)))` returns both `C1*exp(-x)` and `C1*exp(x)` in SymPy 1.14.0. With `C1 = 1`, the decreasing exponential has residual `-2` at `x = 0`, so it is not a solution.

## Search Queries

- `SymPy dsolve f'(x) sqrt(f(x)**2) exp(-x) bug`
- `site:github.com/sympy/sympy/issues "sqrt(f(x)**2)" "dsolve"`
- `"dsolve" "sqrt(f(x)**2)" "SymPy"`
- `"sqrt(f(x)**2)" "dsolve"`
- `"f'(x)" "sqrt(f(x)**2)" "SymPy"`

## Closest Matches

- SymPy ODE documentation: https://docs.sympy.org/latest/modules/solvers/ode.html#sympy.solvers.ode.dsolve describes `dsolve` as solving supported ordinary differential equations.
- SymPy `sqrt` documentation: https://docs.sympy.org/latest/modules/functions/elementary.html#sympy.functions.elementary.miscellaneous.sqrt documents that `sqrt(x**2)` is not generally equal to `x` because `sqrt` is the principal square root.
- General square-root reference: https://en.wikipedia.org/wiki/Square_root notes that `sqrt(x**2) = |x|` for real `x`, which is the mathematical source of the missing sign condition.

## Similarity Analysis

The public material establishes the broad branch/sign issue: replacing `sqrt(u**2)` by `u` or by unrestricted `+/-u` is not valid without assumptions. That is directly related to the ODE solver accepting both exponential branches without conditions on the sign or branch of `f(x)`.

Focused searches did not find a public report for `dsolve(Eq(diff(f(x), x), sqrt(f(x)**2)))`, the invalid `C1*exp(-x)` branch, or a residual check failure for this ODE.

## Specific Novelty Assessment

The underlying square-root branch family is known. The specific ODE solver output containing an invalid decreasing exponential branch appears not to be publicly reported.

## Recommendation

continue_to_artifact_generation
