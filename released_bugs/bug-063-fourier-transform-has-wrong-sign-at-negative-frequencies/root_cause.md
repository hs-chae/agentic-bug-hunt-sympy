---
diagnosis_status: narrowed
confidence: 76
location: sympy/integrals/meijerint.py:1834 and sympy/integrals/meijerint.py:2048
---

## Candidate Summary

`fourier_transform(cos(x)/(x**2 + 1), x, k)` gives the wrong sign at negative real frequencies. At `k = -1/3`, the public transform evaluates to the negative of the shift-theorem value.

## Call Path

The public call is:

`fourier_transform(f, x, k)` -> `FourierTransform(f, x, k).doit()` -> `FourierTypeTransform._compute_transform` -> `_fourier_transform(f, x, k, 1, -2*pi, "Fourier")`.

`_fourier_transform` forms:

`integrate(f*exp(-2*pi*I*x*k), (x, -oo, oo))`

That definite integral is evaluated by the Meijer integration path:

`Integral.doit` / `integrate` -> `meijerint_definite` -> split `-oo..oo` at zero -> `_meijerint_definite_2` on the two half-line integrals `exp(-2*pi*I*k*x)*cos(x)/(x**2+1)` and `exp(2*pi*I*k*x)*cos(x)/(x**2+1)` -> `_meijerint_definite_4` -> two-Meijer-G rewrite and integration.

The final public result is then passed through `sympy/integrals/transforms.py:_simplify`, which applies `powdenest(piecewise_fold(expr), polar=True)` and `simplify`.

## Root Cause

I narrowed the source to the Meijer definite integration result produced under `sympy/integrals/meijerint.py`, especially:

```python
# meijerint_definite, -oo to oo case
res1 = _meijerint_definite_2(f.subs(x, x + c), x)
res2 = _meijerint_definite_2(f.subs(x, c - x), x)
res = res1 + res2
```

and the two-Meijer-G evaluation path:

```python
# _meijerint_definite_4
gs = _rewrite2(f, x)
...
res += fac*_int0oo(f1, f2, x)
```

with `_int0oo` returning:

```python
eta, _ = _get_coeff_exp(g1.argument, x)
omega, _ = _get_coeff_exp(g2.argument, x)
return meijerg(a1, a2, b1, b2, omega/eta)/eta
```

The generated half-line formulas contain branch-sensitive factors involving `polar_lift(k)**2`, `Abs(k)`, and an explicit denominator `k`. After transform simplification, the result retains an overall `Abs(k)/k` sign factor. That makes the transform odd under `k -> -k`, even though the input function is even and real.

I did not pin a single faulty line beyond the Meijer integration branch construction. The bad sign is already present before `_fourier_transform` returns; `_simplify` makes it into the reproducible public expression, but it is not the first source of the incorrect branch dependence.

## Mechanism

With internal debug enabled, `meijerint_definite` splits the integral at zero and separately rewrites the two half-line integrals with exponential factors `exp(-2*pi*I*k*x)` and `exp(2*pi*I*k*x)`. The debug trace shows `_rewrite2` converting each half-line integral into products of Meijer-G functions whose arguments contain:

`pi**2*exp_polar(±I*pi)*polar_lift(k)**2`

and later:

`polar_lift(k)**2*polar_lift(1 - 1/(2*pi*Abs(k)))**2`

The returned expression has terms divided by `k*(...)`. The default transform simplification rewrites this to a compact expression with a visible prefactor:

`... * Abs(k) / k / ...`

At `k = 1/3`, this factor is `+1` and the numeric value matches the expected positive transform. At `k = -1/3`, the factor is `-1`, producing the negative result. The mathematically correct Fourier transform from the shift theorem depends on `Abs(2*pi*k ± 1)` and is positive/even; it should not contain `Abs(k)/k`.

## Suggested Fix Direction

The Meijer definite integration path should preserve the sign/branch assumptions for the real frequency parameter. For this transform family, either the half-line Meijer result needs a branch correction when `k` is real negative, or the integration/simplification should return a `Piecewise`/absolute-value expression equivalent to the even shift-theorem form instead of a formula with `Abs(k)/k`.

As a narrower practical guard, `_fourier_transform` could avoid accepting a Meijer result whose conditions do not distinguish the `k < 0` branch correctly, but the underlying source is in the Meijer integration formula generation.

## Confidence and Caveats

Confidence is moderate. The call path and bad intermediate expressions were traced with pinned SymPy 1.14.0, and the wrong `Abs(k)/k` dependence is visible in the returned transform. I did not reduce the Meijer machinery to a minimal local theorem failure, so this is reported as narrowed rather than fully located.
