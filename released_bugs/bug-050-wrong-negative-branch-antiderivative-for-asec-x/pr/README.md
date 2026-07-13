# Fix integrate(asec(x), x) on the negative real branch

## Summary

`integrate(asec(x), x)` currently returns an antiderivative whose derivative is
incorrect for real `x < -1`. The returned expression differentiates correctly on
the positive branch, but on the negative branch it contains the wrong sign for
the Meijer/hyperexpand primitive of `1/(x*sqrt(1 - 1/x**2))`.

## Reproducer

```python
from sympy import *

x = symbols("x", real=True)
residual = diff(integrate(asec(x), x), x) - asec(x)
print(simplify(residual.subs(x, -2)))
```

Current output:

```text
-2*sqrt(3)/3
```

## Expected Behavior

The residual should be `0` at every nonsingular point where the antiderivative is
valid, including `x = -2`.

## Evidence

On SymPy 1.14.0, the returned primitive is:

```text
x*asec(x) - Piecewise((x*acosh(Abs(x))/Abs(x) - I*pi*x/(2*Abs(x)), x**2 > 1), (-I*x*asin(Abs(x))/Abs(x), True))
```

For `x < -1`, the `x*acosh(Abs(x))/Abs(x)` term has the opposite derivative sign
from the needed primitive of `1/(x*sqrt(1 - 1/x**2))`. The proposed regression
test checks the representative case and five additional negative real inputs.

## Suggested Regression Test

Add `pr/tests/test_bug_050_integrate-asec-x-x-differentiates-to-the-wrong-value-on-nega.py`
or move its parametrized test into the appropriate SymPy integration test file.
