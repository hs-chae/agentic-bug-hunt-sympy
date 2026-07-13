# Fix Laplace transform of symbolic closing Heaviside step

## Summary

`laplace_transform(Heaviside(a - t), t, s, noconds=True)` currently returns `exp(-a*s)/s`. After substituting a positive cutoff, for example `a = 2`, this gives `exp(-2*s)/s`, but the transform of `Heaviside(2 - t)` over `t >= 0` is `(1 - exp(-2*s))/s`.

## Reproducer

```python
from sympy import Heaviside, exp, integrate, laplace_transform, symbols

t = symbols("t", real=True)
s = symbols("s", positive=True)
a = symbols("a")

F = laplace_transform(Heaviside(a - t), t, s, noconds=True)
print(F)
print(F.subs(a, 2))
print(integrate(exp(-s*t), (t, 0, 2)))
```

Current output:

```text
exp(-a*s)/s
exp(-2*s)/s
1/s - exp(-2*s)/s
```

## Expected Behavior

For positive `a`, `Heaviside(a - t)` is one on `0 <= t < a`, so the transform should specialize to

```text
(1 - exp(-a*s))/s
```

For symbolic `a`, the transform should preserve the relevant conditions instead of returning a formula that becomes wrong after substitution.

## Evidence

The returned conditional transform is:

```text
(exp(-a*s)/s, 0, (a > 0) & (a < 0) & Ne(1/a, 0))
```

With `noconds=True`, the contradictory condition is dropped and only the invalid expression remains. The attached regression test checks the representative `a = 2` specialization plus five additional positive cutoffs.

## Suggested Regression Test

See `pr/tests/test_bug_016_laplace_transform_of_heaviside_a_t_uses_the_wrong_cutoff.py`.
