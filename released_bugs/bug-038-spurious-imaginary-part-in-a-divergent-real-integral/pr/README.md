# Fix integrate adds a spurious imaginary part to the divergent real integral of 1/Abs(x)

## Summary

This PR should correct a SymPy 1.14.0 correctness bug in `definite integration / improper integrals`.

## Reproducer

```python
integrate(1/Abs(x), (x, -1, 0))
```

Current behavior: integral = oo + I*pi

Expected behavior: oo, with no imaginary component.

## Evidence

The artifact bundle contains `reproduce_bug.py` for the minimal failure and `related_bugs.py` for the representative case plus five additional instantiations with an independent oracle. The mathematical issue is: For x in [-a, 0), 1/Abs(x) = -1/x. The truncated integral from -a to -epsilon is log(a/epsilon), which tends to positive real infinity.

## Suggested regression test

Add `pr/tests/test_bug_038_integrate-adds-a-spurious-imaginary-part-to-the-divergent-re.py` or move its parametrized test into the appropriate SymPy test module.
