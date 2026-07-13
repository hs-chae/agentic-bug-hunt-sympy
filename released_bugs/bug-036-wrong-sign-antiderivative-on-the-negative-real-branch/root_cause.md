---
diagnosis_status: narrowed
confidence: 75
location: sympy/integrals/meijerint.py:1736
---

## Candidate Summary

`integrate(1/(x*sqrt(x**2 + 1)), x)` returns `-asinh(1/x)`. Its derivative is positive at `x = -2`, while the integrand is negative there.

## Call Path

The default `integrate` path in `sympy/integrals/integrals.py` tries several methods. For this integrand, `heurisch`, manual integration, and Risch do not produce an answer; `integrate(..., meijerg=False)` remains unevaluated. The result comes from `meijerint_indefinite`.

`meijerint_indefinite` calls `_meijerint_indefinite_1`, which calls `_rewrite1`. For the reproducer, `_rewrite1` returns:

`(1, 1/x, [(1/sqrt(pi), 0, meijerg(((1/2,), ()), ((0,), ()), x**2))], True)`.

So the integrand is represented as `x**-1` times a Meijer G function of `x**2`.

## Root Cause

The cause is narrowed to the branch-blind indefinite Meijer substitution in `sympy/integrals/meijerint.py`, `_meijerint_indefinite_1`, lines 1704-1740, especially:

```python
a, b = _get_coeff_exp(g.argument, x)
_, c = _get_coeff_exp(po, x)
...
fac_ = fac * C * x**(1 + c) / b
rho = (c + 1)/b
...
r = hyperexpand(r.subs(t, a*x**b), place=place)
res += powdenest(fac_*r, polar=True)
```

For this input, the substitution is effectively `t = x**2` with `po = 1/x`. The resulting Meijer antiderivative is hyperexpanded to `-asinh(1/x)` without a branch/sign condition for the two real branches of `x`.

## Mechanism

The formal substitution through `x**2` is not branch-neutral for an indefinite integral involving `1/x`. On the positive real branch, `-asinh(1/x)` differentiates to the original integrand. On the negative real branch, differentiating it gives the opposite sign because `sqrt(1 + x**(-2))` and `sqrt(x**2 + 1)/x` differ by a sign when `x < 0`.

The Meijer integration code returns a single expression valid on one branch, but the public indefinite integral is presented without that branch restriction.

## Suggested Fix Direction

The Meijer indefinite path should avoid branch-losing substitutions like `x -> x**2` for odd powers such as `1/x` unless it can return a piecewise/conditional antiderivative. At minimum, it should verify the derivative against the original integrand under real branch assumptions or decline this Meijer result when the check is branch-dependent.

## Confidence and Caveats

Moderate confidence. The method source is clearly localized: disabling Meijer integration suppresses the result, and `_meijerint_indefinite_1` directly returns `-asinh(1/x)`. I did not derive every internal Meijer transformation identity, so I mark this as narrowed rather than fully located to one algebraic line.
