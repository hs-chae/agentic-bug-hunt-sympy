---
diagnosis_status: located
confidence: 92
location: sympy/solvers/solveset.py:284
---

## Candidate Summary

`solveset(Eq(x**Rational(2, 3), 4), x, S.Reals)` returns `{-8, 8}` even though `(-8)**(2/3)` is a non-real principal-power value in SymPy.

## Call Path

`solveset(Eq(x**(2/3), 4), x, S.Reals)` normalizes to solving `x**(2/3) - 4 = 0`.

In `sympy/solvers/solveset.py`, `_solveset` treats the expression as a polynomial in the generator `x**(2/3)`. After solving the polynomial for that generator, lines 1057-1062 call `invert_real(gen, y, symbol)` to map solutions for `y = x**(2/3)` back to `x`.

`invert_real` delegates to `_invert_real`, whose rational-power branch handles `x**(2/3)`.

## Root Cause

The faulty logic is in `sympy/solvers/solveset.py`, `_invert_real`, lines 284-289:

```python
if den % 2 == 1:
    root = Lambda(n, real_root(n, expo))
    res = imageset(root, g_ys)
    if num % 2 == 0:
        neg_res = imageset(Lambda(n, -n), res)
        return _invert_real(base, res + neg_res, symbol)
```

For exponent `2/3`, `den` is odd and `num` is even, so `_invert_real(x**(2/3), y, x)` returns both `y**(3/2)` and `-y**(3/2)`. This is the inverse of the real-valued expression `(real_cuberoot(x))**2`, not SymPy's principal complex power `x**Rational(2, 3)`.

There is no subsequent residual check against the original principal-power expression before returning the finite set.

## Mechanism

With `y = 4`, `_invert_real` maps `x**(2/3) = 4` to `x = 8` and `x = -8`. The positive solution is valid. The negative solution is valid only for real-root semantics; under SymPy principal powers,

`(-8)**(2/3) = 4*(-1)**(2/3) = -2 + 2*sqrt(3)*I`,

so the residual is nonzero and non-real. The real-domain solver has inverted a different function than the one represented by the original expression.

## Suggested Fix Direction

The rational-power inversion should distinguish principal `Pow` semantics from real-root semantics. For principal powers with even numerator and odd denominator, negative inverse branches should be filtered or guarded unless the expression explicitly uses `real_root`.

## Confidence and Caveats

Confidence is high. A direct helper probe produced `_invert_real(x**(2/3), y, x) -> (x, Intersection({-y**(3/2), y**(3/2)}, Reals))`, exactly explaining `{-8, 8}`.
