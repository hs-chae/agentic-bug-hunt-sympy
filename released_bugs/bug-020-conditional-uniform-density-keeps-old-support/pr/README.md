# Fix conditional Uniform density support

## Summary

`density(given(U, U > t))` for a continuous uniform random variable currently renormalizes the original density but does not restrict the density support to the conditioning event. For `U ~ Uniform(0, 1)` and `t = 1/2`, the returned density integrates to `2`.

## Reproducer

```python
from sympy import S, integrate, oo, symbols
from sympy.stats import Uniform, density, given

x = symbols("x")
U = Uniform("U", 0, 1)
d = density(given(U, U > S.Half))(x)

assert integrate(d, (x, -oo, oo)) == 1
assert integrate(d, (x, 0, S.Half)) == 0
```

## Expected behavior

The conditional density should be `2` on `[1/2, 1]` and `0` elsewhere.

## Evidence

The current output is `2*Piecewise((1, (x >= 0) & (x <= 1)), (0, True))`, whose total mass is `2` and whose mass below `1/2` is `1`.

## Suggested regression test

Add `pr/tests/test_bug_020_density_given_uniform_0_1_u_1_2_has_the_wrong_support_and_to.py`, which parametrizes several thresholds and checks normalization and zero density below the conditioning threshold.
