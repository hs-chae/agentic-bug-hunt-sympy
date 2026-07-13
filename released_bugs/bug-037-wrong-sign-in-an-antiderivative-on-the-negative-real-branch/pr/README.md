# Fix integrate returns an antiderivative with the wrong sign for 1/(x*sqrt(x**2 - 1)) on negative reals

## Summary

This PR should correct a SymPy 1.14.0 correctness bug in `integrals / branch cuts`.

## Reproducer

```python
integrate(1/(x*sqrt(x**2 - 1)), x)
```

Current behavior: At x=-3, integrand = -0.1178511301977579 but derivative of returned antiderivative = +0.1178511301977579.

Expected behavior: The derivative of any returned antiderivative must equal 1/(x*sqrt(x**2 - 1)) on ordinary branch points.

## Evidence

The artifact bundle contains `reproduce_bug.py` for the minimal failure and `related_bugs.py` for the representative case plus five additional instantiations with an independent oracle. The mathematical issue is: On x < -1 the principal sqrt(x**2 - 1) is positive and x is negative, so the integrand is negative. The derivative of SymPy's fallback branch -asin(1/x) is positive there.

## Suggested regression test

Add `pr/tests/test_bug_037_integrate-returns-an-antiderivative-with-the-wrong-sign-for-.py` or move its parametrized test into the appropriate SymPy test module.
