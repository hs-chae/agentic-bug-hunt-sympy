---
diagnosis_status: located
confidence: 90
location: sympy/core/add.py:1067
---

## Candidate Summary

`limit(diff(besselj(1, x)/x, x), x, 0)` returns `-oo`, but the series of `besselj(1, x)/x` is `1/2 - x**2/16 + O(x**4)`, so its derivative tends to `0`.

## Call Path

The public call differentiates `besselj(1, x)/x`, using `BesselBase.fdiff` in `sympy/functions/special/bessel.py:66-70`. That derivative is correct:

```python
(besselj(0, x)/2 - besselj(2, x)/2)/x - besselj(1, x)/x**2
```

The wrong result appears in `limit`. `Limit.doit` in `sympy/series/limits.py` sees the expression as meromorphic at zero and calls `newe.leadterm(z, cdir=cdir)` at `limits.py:304-312`. That reaches `Add._eval_as_leading_term` in `sympy/core/add.py`.

## Root Cause

The responsible step is the cancellation fallback in `Add._eval_as_leading_term`, especially lines 1067-1078:

```python
n0 = min.getn()
...
while res.is_Order:
    res = old._eval_nseries(x, n=n0+incr, logx=logx, cdir=cdir).cancel().powsimp().trigsimp()
    incr *= 2
return res.as_leading_term(x, logx=logx, cdir=cdir)
```

For this expression, the initial leading terms `1/(2*x)` and `-1/(2*x)` cancel, so this fallback is invoked. However, `min.getn()` is `-1`, so the first non-`Order` series requested is with `n = 0`. The Bessel series at that order is still truncated as `-1/(2*x) + O(1)`, even though a higher-order expansion gives `-x/8 + O(x**2)`.

## Mechanism

The expanded derivative has leading pieces:

```python
besselj(0, x)/(2*x)      ->  1/(2*x)
-besselj(1, x)/x**2      -> -1/(2*x)
-besselj(2, x)/(2*x)     -> -x/16
```

`Add._eval_as_leading_term` correctly detects that the two `1/x` pieces cancel. But it then asks `_eval_nseries` for too low an order. At `n = 0`, the truncated Bessel expansion has not included enough terms from `besselj(0, x)` and `besselj(1, x)` to expose the next nonzero term, so it returns a spurious leading term `-1/(2*x)`. `Limit.doit` receives exponent `-1` and coefficient `-1/2`, and therefore returns `-oo`.

## Suggested Fix Direction

When the first leading term of an `Add` cancels, the fallback should request enough extra series terms to move past the canceled order before accepting a non-`Order` result. In this case, increasing the requested order to at least `2` exposes the true leading term `-x/8`.

## Confidence and Caveats

High confidence. The derivative formula is correct, and direct probing of `_eval_nseries` shows `n = 0` gives the bad `-1/(2*x)` while `n = 2` gives the correct leading term.
