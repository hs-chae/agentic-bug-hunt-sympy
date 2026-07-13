---
diagnosis_status: located
confidence: 91
location: sympy/solvers/solveset.py:178
---

## Candidate Summary

`solveset(Eq(exp(I*x), 1), x, Interval(0, 2*pi))` returns `{0}`. Since the domain is closed, `2*pi` also satisfies the equation and should be included.

## Call Path

Public call:

`solveset(Eq(exp(I*x), 1), x, Interval(0, 2*pi))`

Internal path:

`solveset` rewrites the equation to solving `exp(I*x) - 1 = 0`, creates a real dummy symbol because the domain is a subset of `S.Reals`, and calls `_solveset`.

`_solveset` reaches the generic inversion branch at `sympy/solvers/solveset.py:1313`:

```python
lhs, rhs_s = inverter(f, 0, symbol)
```

where `inverter` is `_invert(f, rhs, symbol, domain)`. `_invert` chooses `_invert_real` because the domain is a subset of reals.

## Root Cause

The responsible code is `sympy/solvers/solveset.py`, `_invert`, lines 178-181:

```python
if domain.is_subset(S.Reals):
    x1, s = _invert_real(f_x, FiniteSet(y), x)
else:
    x1, s = _invert_complex(f_x, FiniteSet(y), x)
```

This chooses the real exponential inverter based on the solution domain, not on whether `exp(I*x)` is a real-valued one-to-one exponential. `_invert_real` then applies the single-valued log rule for `exp` at lines 225-228. For the reproducer this reduces `exp(I*x) = 1` to `I*x = 0`, hence `x = 0`.

The complex inverter does know the periodic family:

`invert_complex(exp(I*x), 1, x)` gives `ImageSet(Lambda(_n, 2*_n*pi), Integers)`.

But it is not used for real domains.

## Mechanism

The correct solution set before intersecting the interval is `{2*pi*n | n in Integers}`. Intersecting with `Interval(0, 2*pi)` should produce `{0, 2*pi}`.

Instead, `_invert_real` loses the integer parameter during inversion and returns only `{0}`. Once `_solveset` has the finite set `{0}`, the final domain intersection/checking cannot recover the missing endpoint `2*pi`.

## Suggested Fix Direction

For equations involving `exp` with non-real or periodic arguments, especially `exp(I*real_symbol)`, solveset over real domains should use complex exponential inversion and then intersect the resulting periodic image set with the real domain. The `_invert` dispatch should consider the expression's value/argument structure, not only `domain.is_subset(S.Reals)`.

## Confidence and Caveats

High confidence. Direct probes show `_solveset(exp(I*x)-1, x, Interval(0, 2*pi))` returns `{0}`, `invert_real(exp(I*x), 1, x)` returns `{0}`, and `invert_complex(exp(I*x), 1, x)` returns the missing periodic family.
