---
diagnosis_status: located
confidence: 92
location: sympy/integrals/transforms.py:945-961
---

## Candidate Summary

`inverse_fourier_transform(2/(1 + 4*pi**2*w**2), w, t)` returns `exp(-t)`.  The correct inverse transform is the even function `exp(-Abs(t))`; the returned expression is wrong for negative real `t`.

## Call Path

The public call `inverse_fourier_transform(F, w, t)` constructs `InverseFourierTransform(F, w, t)` in `sympy/integrals/transforms.py:1066-1105`.  `InverseFourierTransform._compute_transform` inherits `FourierTypeTransform._compute_transform` at `transforms.py:975-978`, which calls `_fourier_transform(F, w, t, 1, 2*pi, "Inverse Fourier", ...)`.

Inside `_fourier_transform`, SymPy evaluates the full real-axis integral

`integrate(F*exp(2*pi*I*w*t), (w, -oo, oo))`.

For this reproducer, that integral returns a `Piecewise` whose first branch is a closed form under condition `t > 0`, and whose fallback branch is the original unevaluated integral.

## Root Cause

The responsible code is `sympy/integrals/transforms.py:_fourier_transform`, especially lines `945-961`.

When the integral result is a `Piecewise`, lines `954-961` do this:

1. Require that `F` is a `Piecewise`.
2. Take only `F.args[0]`, i.e. the first branch.
3. Return that branch expression and its condition.

For this integral, the first branch is only valid for `t > 0`.  The code does not preserve the fallback unevaluated branch, does not ask for or compute the corresponding `t < 0` branch, and does not reconstruct an even or conditional result.  The public Fourier transform wrapper defaults to `noconds=True` via `_noconds_(True)` at `transforms.py:933`, so the condition `t > 0` is dropped by the decorator at `transforms.py:244-248`.

## Mechanism

The raw kernel integral for the reproducer is a `Piecewise((closed_form, t > 0), (Integral(...), True))`.  `_fourier_transform` selects only the `t > 0` closed form.  `_simplify` at `transforms.py:216-220` simplifies that branch to `exp(-t)`.  Because `inverse_fourier_transform` uses `noconds=True` by default, the caller receives `exp(-t)` without the condition `t > 0`.

That branch agrees with `exp(-Abs(t))` only when `t >= 0`.  At `t = -1`, it evaluates to `E` instead of `exp(-1)`.

## Suggested Fix Direction

Do not collapse a `Piecewise` transform integral to only its first branch unless the condition is globally true for the transform variable/domain.  For Fourier transforms, preserve the conditional result, compute the missing branch, or return an unevaluated transform when the only closed-form branch is conditional and `noconds=True` would hide that condition.

## Confidence and Caveats

Confidence is high.  The probe confirmed that `_fourier_transform(..., noconds=False)` returns the positive-`t` branch with condition `t > 0`, while the public default drops that condition.  I did not identify a separate integration bug here; the transform wrapper mishandles the conditional integral result.
