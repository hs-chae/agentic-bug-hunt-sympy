---
diagnosis_status: located
confidence: 90
location: sympy/core/expr.py:962-991
---

## Candidate Summary

`integrate(1/Abs(x), (x, -1, 0))` with `x` real returns `oo + I*pi`.  The improper integral is real and diverges to positive infinity, so the finite imaginary term is spurious.

## Call Path

The public definite integral enters `Integral.doit` in `sympy/integrals/integrals.py`.  Because the integrand contains `Abs`, lines `539-546` rewrite it as a `Piecewise` over a real dummy:

`Piecewise((1/x, x >= 0), (-1/x, True))`.

The Piecewise antiderivative path then integrates to an antiderivative equivalent to:

`Piecewise((-log(x), x <= 0), (log(x), True))`.

The definite interval is evaluated by `Integral.doit` at `integrals.py:704-719`, which calls `_eval_interval` on the antiderivative.  The actual endpoint evaluation is in `sympy/core/expr.py:_eval_interval`.

## Root Cause

The responsible code is `sympy/core/expr.py:962-991`, used via `Piecewise._eval_interval` at `sympy/functions/elementary/piecewise.py:454-582`.

For an endpoint, `_eval_interval` first substitutes the endpoint:

```python
C = self.subs(x, c)
```

Only if that substitution is infinite/NaN does it replace it with a one-sided limit.  At the lower endpoint `x = -1`, substituting into the negative-branch antiderivative `-log(x)` gives `-I*pi` from the principal complex logarithm.  That is finite, so `_eval_interval` keeps it.  At `x -> 0-`, the one-sided limit is `oo`.  The interval value becomes:

`oo - (-I*pi) = oo + I*pi`.

The algorithm evaluates a real-branch antiderivative with the principal complex `log(x)` instead of respecting that `-log(x)` came from integrating `-1/x` on the negative real interval, where it should behave as `-log(-x)` up to a real constant.

## Mechanism

On `[-1, 0)`, `1/Abs(x) = -1/x`.  A real antiderivative is `-log(-x)`, and the truncated integral from `-1` to `-eps` is `-log(eps)`, which tends to `oo`.

SymPy's Piecewise integration uses `-log(x)` for the negative branch.  That expression differentiates to `-1/x`, but it carries the principal-log value `log(-1) = I*pi` at the finite endpoint.  `_eval_interval` subtracts that branch constant and reports the imaginary residue.

## Suggested Fix Direction

When evaluating a Piecewise antiderivative on a real interval, endpoint values should be taken as one-sided limits within the active real branch, or the antiderivative for `-1/x` on `x < 0` should be represented as `-log(-x)`/`-log(Abs(x))` rather than principal `-log(x)`.  More generally, `_eval_interval` should not retain finite principal-log branch constants for real improper integrals of real integrands.

## Confidence and Caveats

Confidence is high.  A probe showed `Piecewise((-log(x), x <= 0), (log(x), True))._eval_interval(x, -1, 0)` returns `oo + I*pi`, and the `I*pi` comes specifically from `(-log(x)).subs(x, -1)`.
