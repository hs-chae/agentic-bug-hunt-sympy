# infinite telescoping Sum ignores undefined initial terms and returns -1

## Summary

This PR should fix a correctness bug in concrete / summation / convergence and singular terms. The current code returns a mathematically incorrect result for `Sum(1/(k*(k - 1)), (k, 0, oo)).doit()`.

## Reproducer

See `../reproduce_bug.py` for the checkout-pinned minimal reproducer. The observed wrong output is:

```text
Sum(1/(k*(k - 1)), (k, 0, oo)).doit() -> -1 despite undefined terms at k = 0 and k = 1
```

## Expected behavior

The sum from k = 0 to infinity should not evaluate to the finite value -1 because the terms at k = 0 and k = 1 are undefined.

## Evidence

`../related_bugs.py` exercises the representative case plus five additional instantiations and performs an independent check for each one. On the buggy checkout it reports `Incorrect`.

## Suggested regression test

Add `tests/test_bug_017_infinite_telescoping_sum_ignores_undefined_initial_terms_and.py` or fold the parametrized test into the nearest existing SymPy test module.
