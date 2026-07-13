# Fix even powers of non-real complex sign

## Summary

`sign(z)**2` currently evaluates to `1` for nonzero non-real complex numbers such as `z = 1 + I`. This applies the real identity `sign(x)**2 = 1` outside its domain. For complex `z`, SymPy documents `sign(z)` as the complex direction `z/Abs(z)`, so the square should be `z**2/Abs(z)**2`.

## Reproducer

```python
from sympy import Abs, I, N, sign

z = 1 + I
actual = sign(z)**2
expected = z**2 / Abs(z)**2

print(actual)
print(expected)
print(N(actual, 50))
print(N(expected, 50))
```

Current output:

```text
1
(1 + I)**2/2
1.0000000000000000000000000000000000000000000000000
1.0*I
```

## Expected behavior

The expression should either remain unevaluated until a valid complex-direction evaluation is possible, or evaluate consistently with `sign(z) = z/Abs(z)`. It should not collapse to `1` for non-real complex `z`.

## Evidence

For `z = 1 + I`, the definition gives:

```text
sign(z)**2 = (z/Abs(z))**2 = (1 + I)**2 / 2 = I
```

The included regression test covers the representative input and five additional non-real complex values.

## Suggested regression test

Add `pr/tests/test_bug_040_even_powers_of_complex_sign_collapse_to_one.py` to the relevant elementary complex function tests, or adapt its parametrized test into the existing `sign` test file.
