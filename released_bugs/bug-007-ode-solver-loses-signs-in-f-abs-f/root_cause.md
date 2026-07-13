---
diagnosis_status: narrowed
confidence: 78
location: sympy/solvers/ode/ode.py:1666
---

## Candidate Summary

`dsolve(Eq(f'(x), sqrt(f(x)**2)))` returns both `C1*exp(-x)` and `C1*exp(x)`. The branch `f(x)=exp(-x)` fails the ODE because its derivative is negative while `sqrt(exp(-2*x))` is positive.

## Call Path

`classify_ode` classifies the equation as `separable`, `1st_exact`, and other hints. The default result comes from the separable/exact simplification path.

For the separable hint, `sympy/solvers/ode/single.py`, class `Separable`, builds the implicit solution at lines 1287-1293:

`Integral(1/sqrt(_y**2), (_y, f(x))) = C1 + Integral(1, x)`.

`odesimp` then calls `_handle_Integral`, which evaluates the left integral to:

`f(x)*log(f(x))/sqrt(f(x)**2) = C1 + x`.

Finally `odesimp` calls `solve(eq, func, force=True, ...)` at `sympy/solvers/ode/ode.py:1666`, producing the two explicit branches `C1*exp(-x)` and `C1*exp(x)`.

## Root Cause

The narrowed source-level cause is the ODE simplification step in `odesimp`, lines 1633 and 1663-1684, especially the unconditional explicit solve:

```python
eq = _handle_Integral(eq, func, hint)
...
eqsol = solve(eq, func, force=True, rational=False if floats else None)
...
eq = [Eq(f(x), _expand(t)) for t in eqsol]
```

The implicit equation contains the branch-sensitive term `sqrt(f(x)**2)`. Solving it explicitly introduces branches without retaining the sign/branch condition on `f(x)`. The decreasing exponential is valid only on a negative branch of `f`, but the returned expression `C1*exp(-x)` is unconstrained, so `C1=1` is falsely allowed.

## Mechanism

The separable setup effectively integrates `df/sqrt(f**2) = dx`. On real-valued branches, `sqrt(f**2) = Abs(f)`, so the sign of `f` matters. Positive solutions satisfy `f' = f` and give increasing exponentials. Negative solutions satisfy `f' = -f` and give decreasing exponentials with a negative multiplicative constant.

`odesimp` solves the evaluated implicit equation algebraically and returns both exponentials with an arbitrary unrestricted constant. This drops the condition needed for the `exp(-x)` branch, so substituting `C1=1` produces a false solution.

## Suggested Fix Direction

When an implicit ODE solution contains branch-sensitive terms such as `sqrt(f(x)**2)`, `odesimp` should not call `solve(..., force=True)` into unconstrained explicit branches unless it can attach the necessary constant/sign conditions. A post-solve `checkodesol`-style validation for representative constant assumptions would also catch the unrestricted positive `C1*exp(-x)` branch.

## Confidence and Caveats

Moderate confidence. The bad branch is produced during `odesimp` explicit solving of a branch-sensitive implicit separable solution. I did not fully trace the internal `solve` branch generation, so I mark this as narrowed rather than assigning the root solely to `solve`.
