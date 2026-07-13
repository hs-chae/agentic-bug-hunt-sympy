---
diagnosis_status: narrowed
confidence: 78
location: sympy/integrals/meijerint.py:1653-1777
---

## Candidate Summary

`integrate(1/(x*sqrt(x**2 - 1)), x)` returns `Piecewise((I*acosh(1/x), 1/Abs(x**2) > 1), (-asin(1/x), True))`.  On the negative real branch, differentiating the `-asin(1/x)` branch gives the opposite sign of the original integrand.

## Call Path

The public call `integrate(g, x)` constructs an `Integral` and calls `Integral.doit`.  Indefinite integration reaches `Integral._eval_integral` in `sympy/integrals/integrals.py:823-1164`.

The ordinary Risch and heuristic paths do not handle this algebraic integrand.  The Meijer-G fallback at `integrals.py:1102-1109` calls `meijerint_indefinite(g, x)`.  A probe showed:

`meijerint_indefinite(1/(x*sqrt(x**2 - 1)), x)` returns the same bad `Piecewise` as `integrate(..., meijerg=True)`.

## Root Cause

The cause is narrowed to `sympy/integrals/meijerint.py:meijerint_indefinite` and `_meijerint_indefinite_1`, especially lines `1695-1777`.

That code rewrites the algebraic integrand as a Meijer G expression, applies a generic antiderivative formula, expands it with `hyperexpand` at `meijerint.py:1736`, combines powers using `powdenest(..., polar=True)` at `meijerint.py:1740`, and then removes polar/branch annotations with `_my_unpolarify(_clean(...))` at `meijerint.py:1772-1777`.

The resulting branch `-asin(1/x)` is only a correct antiderivative on the positive real branch outside `[-1, 1]`.  There is no sign/branch guard distinguishing `x > 1` from `x < -1`.

## Mechanism

For `x < -1`, the integrand is negative:

`1/(x*sqrt(x**2 - 1)) < 0`.

But the derivative of the returned fallback branch is

`d(-asin(1/x))/dx = 1/(x**2*sqrt(1 - 1/x**2))`,

which is positive on `x < -1`.  The correct real antiderivative on the negative branch would need the opposite sign, or an explicit branch-aware condition.

The Meijer-G path produces a single fallback branch for `True` after the inner branch `1/Abs(x**2) > 1`; that fallback conflates both real exterior intervals.  The sign of `x` is lost in the conversion from the Meijer/hyperexpanded expression back to ordinary inverse trig functions.

## Suggested Fix Direction

The Meijer indefinite integration result should either retain a sign-dependent `Piecewise` for `x > 1` and `x < -1`, or decline to return a simplified inverse-trig antiderivative when the branch cannot be made valid over the whole fallback condition.  A derivative check over representative real branches would catch this specific regression.

## Confidence and Caveats

Confidence is moderate-high for the source area and mechanism, but I am marking this `narrowed` because I did not isolate the single subroutine inside the Meijer rewrite/hyperexpand/unpolarify sequence that first loses the sign.  The bad result is definitively produced by `meijerint_indefinite`, not by Risch, manual integration, or heuristic Risch.
