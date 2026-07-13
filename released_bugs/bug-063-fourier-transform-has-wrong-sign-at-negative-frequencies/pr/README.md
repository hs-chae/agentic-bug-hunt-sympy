# Fix Fourier transform sign for cos(x)/(x**2 + 1) at negative frequencies

## Summary

`fourier_transform(cos(x)/(x**2 + 1), x, k)` returns the negative of the shift-theorem value at negative frequencies such as `k = -1/3`.

## Reproducer

```python
from sympy import Abs, N, Rational, cos, exp, fourier_transform, pi, symbols

x, k = symbols("x k", real=True)
F = fourier_transform(cos(x)/(x**2 + 1), x, k)
value = Rational(-1, 3)
expected = pi*(exp(-Abs(2*pi*value - 1)) + exp(-Abs(2*pi*value + 1)))/2
print(N(F.subs(k, value), 50))
print(N(expected, 50))
```

## Expected behavior

With SymPy's Fourier convention, `F[1/(x**2+1)](k) = pi*exp(-2*pi*Abs(k))`. Since `cos(x) = (exp(I*x) + exp(-I*x))/2`, the shift theorem gives

```text
pi/2*(exp(-Abs(2*pi*k - 1)) + exp(-Abs(2*pi*k + 1)))
```

This expression is positive and even in the tested negative-frequency cases.

## Evidence

The proposed regression test covers `k = -1/3` plus five additional negative rational frequencies.
