---
diagnosis_status: located
confidence: 86
location: sympy/functions/special/hyper.py:841
---

## Candidate Summary

`integrate(asec(x), x)` returns an antiderivative whose derivative is wrong on the negative real branch. At `x = -2`, `diff(integrate(asec(x), x), x) - asec(x)` simplifies to `-2*sqrt(3)/3`.

## Call Path

The public call is `integrate(asec(x), x)` for a real symbol.

The integration path uses integration by parts for `asec(x)`: `manualintegrate(asec(x), x)` produces `x*asec(x) - Integral(1/(x*sqrt(1 - 1/x**2)), x)`. In default `integrate`, `sympy/integrals/integrals.py:1118-1138` recursively calls `.doit()` on the unevaluated subintegral because manual integration only handled part of the expression.

For the subintegral `1/(x*sqrt(1 - 1/x**2))`, Risch and heurisch do not evaluate it. The Meijer path in `integrals.py:1108-1115` calls `meijerint_indefinite`, which enters `sympy/integrals/meijerint.py:_meijerint_indefinite_1`. There, `_rewrite1` rewrites the radical integrand to a single Meijer G term and `meijerint.py:1736` calls `hyperexpand`.

The internal rewrite for the subintegral is:

```text
(1, 1/x,
 [(1/sqrt(pi), 0,
   meijerg(((1/2,), ()), ((0,), ()), exp_polar(I*pi)/x**2))],
 True)
```

After integrating the G term, `hyperexpand` expands `-meijerg(((1/2,), (1,)), ((0, 0), ()), exp_polar(I*pi)/x**2)`.

## Root Cause

The wrong branch is introduced in the hypergeometric representative expansion, not in `asec.fdiff` or the integration-by-parts rule.

During `hyperexpand`, `HyperRep_asin1._expr_small` and `_expr_big` are called with `z = x**2`. The relevant code is in `sympy/functions/special/hyper.py`:

`HyperRep._eval_rewrite_as_nonrep` at `hyper.py:841-858` chooses a `Piecewise` split using only `abs(x) > 1`.

`HyperRep_asin1._expr_big` at `hyper.py:971-973` returns:

```python
S.NegativeOne**n*((S.Half - n)*pi/sqrt(z) + I*acosh(sqrt(z))/sqrt(z))
```

For `z = x**2`, SymPy simplifies `sqrt(z)` to `Abs(x)` for real `x`. The Slater/hyperexpand prefactor outside this representative is still `x`, so the expanded Meijer primitive contains:

```text
x*acosh(Abs(x))/Abs(x) - I*pi*x/(2*Abs(x))
```

That `x/Abs(x)` factor is valid on the positive branch but flips the derivative on `x < -1`.

## Mechanism

On `|x| > 1`, the radical subintegrand is:

```text
1/(x*sqrt(1 - 1/x**2)) = sign(x)/sqrt(x**2 - 1)
```

A real primitive on both outer intervals is `acosh(Abs(x))` up to constants: its derivative is positive for `x > 1` and negative for `x < -1`.

The Meijer/hyperexpand result instead uses `sign(x)*acosh(Abs(x))` through the multiplier `x/Abs(x)`. On `x < -1`, differentiating that gives the opposite sign for the radical subintegral. The integration-by-parts result subtracts this wrong subintegral, so the final derivative of `x*asec(x) - subprimitive` differs from `asec(x)` by `-2*sqrt(3)/3` at `x = -2`.

The imaginary branch constant in the Piecewise expression does not affect this derivative away from zero; the real `x/Abs(x)` multiplier is the part that causes the residual.

## Suggested Fix Direction

The hyperexpand representative should preserve the correct square-root branch when the continued argument becomes `x**2`, or split the result by the sign of the real variable instead of using only `x**2 > 1`. For this case the real outer-interval primitive should reduce to `acosh(Abs(x))` rather than `x*acosh(Abs(x))/Abs(x)`.

A defensive integration-layer improvement would be to reject a Meijer indefinite result when differentiating it does not recover the integrand under the active assumptions, but the source branch error is in the `HyperRep_asin1` continuation used by `hyperexpand`.

## Confidence and Caveats

Confidence is high for the mechanism and source area. Scratch probes showed that `integrate(subintegrand, meijerg=True)` and `meijerint_indefinite(subintegrand)` produce the same faulty Piecewise result with residual `2*sqrt(3)/3` for the subintegral at `x = -2`. Monkeypatch tracing showed `HyperRep_asin1._expr_big` is called with `z = x**2`, leading directly to the `x/Abs(x)` multiplier. The precise best fix may belong either in the HyperRep continuation formulas or in the Meijer/Slater branch handling around that call.
