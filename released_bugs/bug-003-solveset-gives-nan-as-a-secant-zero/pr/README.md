# Fix solveset(sec(...), Complexes) returning nan as a zero

## Summary

`solveset(sec(x), x, domain=S.Complexes)` currently returns `{nan}`. Since
`sec(z) = 1/cos(z)` and `cos(z)` is finite for every finite complex `z`,
`sec(z)` has no finite complex zeros. The correct result is `EmptySet`.

## Reproducer

```python
from sympy import S, sec, solveset, symbols

x = symbols("x")
print(solveset(sec(x), x, domain=S.Complexes))
```

Actual output on SymPy 1.14.0:

```text
{nan}
```

Expected output:

```text
EmptySet
```

## Evidence

Direct substitution shows that the reported candidate is not a zero:

```python
from sympy import S, sec
print(sec(S.NaN))
```

This prints `nan`, not `0`. The equivalent reciprocal expression
`solveset(1/cos(x), x, domain=S.Complexes)` returns `EmptySet`.

## Suggested Regression Test

The proposed test in `tests/test_bug_003_solveset_sec_x_complexes_returns_nan_as_a_zero.py`
checks the representative case plus shifted, scaled, and affine-argument
instances of the same reciprocal-trigonometric zero pattern.
