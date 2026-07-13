---
diagnosis_status: located
confidence: 82
location: sympy/integrals/meijerint.py:1736
---

## Candidate Summary

`integrate(sqrt(x**2 + 1)/x, x)` returns an antiderivative whose derivative has the wrong sign on negative real `x`. At `x = -2`, the integrand is `-sqrt(5)/2`, but the derivative of SymPy's result is `sqrt(5)/2`.

## Call Path

Public call:

`integrate(sqrt(x**2 + 1)/x, x)`

Internal path:

`integrate` -> `Integral.doit` -> `Integral._eval_integral` in `sympy/integrals/integrals.py`. Risch, heuristic Risch, and manual integration do not produce an answer here. When Meijer-G integration is enabled, `_eval_integral` calls `meijerint_indefinite(g, x)` at `sympy/integrals/integrals.py:1105`.

`meijerint_indefinite` -> `_meijerint_indefinite_1` in `sympy/integrals/meijerint.py`.

Debug tracing showed this rewrite for the reproducer:

```text
could rewrite: (1, 1/x, [(1/gamma(exp_polar(I*pi)/2), 0,
    meijerg(((3/2,), ()), ((0,), ()), x**2))], True)
```

## Root Cause

The responsible area is `sympy/integrals/meijerint.py`, `_meijerint_indefinite_1`, around lines 1703-1740:

```python
a, b = _get_coeff_exp(g.argument, x)
_, c = _get_coeff_exp(po, x)
...
fac_ = fac * C * x**(1 + c) / b
...
r = hyperexpand(r.subs(t, a*x**b), place=place)
res += powdenest(fac_*r, polar=True)
```

For this integrand, the Meijer-G representation uses argument `x**2` (`b = 2`) and power factor `po = 1/x` (`c = -1`). The generic substitution/hyperexpand/powdenest path returns

`x/sqrt(1 + x**(-2)) - asinh(1/x) + 1/(x*sqrt(1 + x**(-2)))`.

That expression is branch-correct only where `sqrt(1 + x**(-2))` corresponds to `sqrt(x**2 + 1)/x`, i.e. on the positive real branch. On negative reals, the original integrand is `sqrt(x**2 + 1)/x = -sqrt(1 + x**(-2))`, but the returned antiderivative differentiates to `+sqrt(1 + x**(-2))`.

## Mechanism

The original integrand can be algebraically written as `sqrt(1 + x**(-2))` only after assuming `x` is positive. In general:

`sqrt(x**2 + 1)/x = sign(x)*sqrt(1 + x**(-2))` on real nonzero `x`.

The Meijer-G rewrite uses `x**2` and then simplifies back through principal powers. The final expression contains `sqrt(1 + x**(-2))`, which is nonnegative for real nonzero `x`; the missing `sign(x)` or branch split causes the derivative to be the positive branch. At `x = -2`, this gives the observed residual `sqrt(5)`.

## Suggested Fix Direction

The Meijer-G indefinite integration path should avoid applying this rewrite globally when the argument substitution uses an even power such as `x**2` and the integrand has an odd power factor such as `1/x`. It should either return a branch-aware/Piecewise antiderivative over `x > 0` and `x < 0`, preserve polar/argument conditions through unpolarification, or decline to evaluate without assumptions.

## Confidence and Caveats

Moderately high confidence. Disabling `meijerg` leaves the integral unevaluated, and direct `meijerint_indefinite` returns the bad antiderivative. I localized the faulty branch loss to the generic Meijer-G substitution and simplification path rather than a single simple conditional.
