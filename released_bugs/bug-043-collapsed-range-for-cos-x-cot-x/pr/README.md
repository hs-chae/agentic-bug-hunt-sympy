# Fix function_range collapses cos(x)/cot(x) to {0} despite nonzero sampled values

## Summary

This PR should prevent SymPy from returning the mathematically incorrect result shown by `bug-report/bug-043-function-range-collapses-cos-x-cot-x-to-0-despite-nonzero-sa`.

## Reproducer

The minimal reproducer is in `reproduce_bug.py`. The current result is:

```text
continuous_domain(...) = Reals; function_range(...) = {0}; value at pi/3 = sqrt(3)/2; range contains sqrt(3)/2 = False
```

## Expected behavior

The real domain should exclude points where cot(x) is undefined or zero, and the range should include values such as sqrt(3)/2.

## Evidence

`related_bugs.py` exercises the representative case plus five additional instantiations and includes direct substitution or independent numerical checks. On the current SymPy 1.14.0 checkout it reports `Incorrect`.

## Suggested regression test

Add `pr/tests/test_bug_043_function-range-collapses-cos-x-cot-x-to-0-despite-nonzero-sa.py` to the relevant SymPy test module, or move the parametrized test into the closest existing test file for calculus / continuous_domain and function_range.
