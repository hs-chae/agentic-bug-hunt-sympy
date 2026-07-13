# Fix integrate(sqrt(x**2 + 1)/x, x) has the wrong derivative sign on negative reals

## Summary

This regression test captures a correctness bug in integrals / indefinite integration / branch cuts.

## Reproducer

```python
integrate(sqrt(x**2 + 1)/x, x)
```

## Expected behavior

The derivative of an antiderivative must equal sqrt(x**2 + 1)/x on every interval where the integrand is defined; at x=-2 it should be -sqrt(5)/2.

## Actual behavior

```text
integrand at -2: -sqrt(5)/2
derivative at -2: sqrt(5)/2
residual at -2: sqrt(5)
```

## Evidence

The artifact bundle contains `reproduce_bug.py` and `related_bugs.py`. The verification script covers the minimal case plus five related instantiations and exits with `Incorrect` on the current buggy version.

## Suggested regression test

Add `pr/tests/test_bug_005_integrate-sqrt-x-2-1-x-x-has-the-wrong-derivative-sign-on-ne.py` to the relevant SymPy test module or fold its parametrized test into the existing tests for the affected subsystem.
