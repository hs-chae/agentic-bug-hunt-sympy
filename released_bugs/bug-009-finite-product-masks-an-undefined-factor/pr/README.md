# Fix product returns 0 for a finite product containing an undefined factor

## Summary

This PR should prevent SymPy from returning the mathematically incorrect result shown by `bug-report/bug-009-product-returns-0-for-a-finite-product-containing-an-undefin`.

## Reproducer

The minimal reproducer is in `reproduce_bug.py`. The current result is:

```text
product(term, (n, 0, 2)) = 0; term values = [0, nan, 0]
```

## Expected behavior

The finite product should be undefined/nan or remain unevaluated with the singular factor exposed.

## Evidence

`related_bugs.py` exercises the representative case plus five additional instantiations and includes direct substitution or independent numerical checks. On the current SymPy 1.14.0 checkout it reports `Incorrect`.

## Suggested regression test

Add `pr/tests/test_bug_009_product-returns-0-for-a-finite-product-containing-an-undefin.py` to the relevant SymPy test module, or move the parametrized test into the closest existing test file for concrete products / finite products.
