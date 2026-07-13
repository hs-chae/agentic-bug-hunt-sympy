# Fix left limit of lerchphi(x, 1, 1) at x = 1 returns an unevaluated divergent endpoint

## Summary

Teach limits/Gruntz to expose the divergent logarithmic behavior of lerchphi(x, 1, a) as x approaches 1 from the left.

## Reproducer

```python
limit(lerchphi(x, 1, 1), x, 1, dir="-")
```

Current result:

```text
limit(lerchphi(x, 1, 1), x, 1, dir='-') = lerchphi(1, 1, 1)
```

Expected result:

```text
oo. For 0 < x < 1, lerchphi(x, 1, 1) = sum_{n>=0} x**n/(n + 1) = -log(1 - x)/x, which diverges to +oo as x -> 1-.
```

## Evidence

The attached `reproduce_bug.py` and `related_bugs.py` scripts demonstrate the issue against the pinned checkout. The verification script covers the representative case plus five additional instantiations and carries an independent numerical/domain check.

## Suggested regression test

Add `pr/tests/test_bug_060_left-limit-of-lerchphi-x-1-1-at-x-1-returns-an-unevaluated-d.py`, or adapt its single parametrized test into the appropriate SymPy test module.
