# Fix inverse_fourier_transform drops the absolute value in the Lorentzian transform pair

## Summary

This PR should correct a SymPy 1.14.0 correctness bug in `integrals.transforms / Fourier transforms`.

## Reproducer

```python
inverse_fourier_transform(2/(1 + 4*pi**2*w**2), w, t)
```

Current behavior: inverse = exp(-t); at t=-1: E

Expected behavior: exp(-Abs(t)); at t=-1: exp(-1)

## Evidence

The artifact bundle contains `reproduce_bug.py` for the minimal failure and `related_bugs.py` for the representative case plus five additional instantiations with an independent oracle. The mathematical issue is: With SymPy Fourier conventions, the transform of exp(-a*Abs(t)) is 2*a/(a**2 + 4*pi**2*w**2). The inverse must be even in t. Returning exp(-a*t) is wrong for negative real t.

## Suggested regression test

Add `pr/tests/test_bug_012_inverse-fourier-transform-drops-the-absolute-value-in-the-lo.py` or move its parametrized test into the appropriate SymPy test module.
