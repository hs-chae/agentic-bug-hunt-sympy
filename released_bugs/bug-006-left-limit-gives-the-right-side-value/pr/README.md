# Fix left-hand Piecewise limit branch selection

## Summary

`limit(Piecewise((0, x < 0), (1, True)), x, 0, dir="-")` returns `1`, but the expression is identically `0` for all sufficiently small negative `x`.

## Reproducer

```python
from sympy import Piecewise, Rational, limit, symbols

x = symbols("x", real=True)
p = Piecewise((0, x < 0), (1, True))
print(limit(p, x, 0, dir="-"))
print(p.subs(x, Rational(-1, 10)))
print(p.subs(x, Rational(1, 10)))
```

Current output:

```text
1
0
1
```

## Expected behavior

The left-hand limit should be `0`.

## Evidence

For all `x` in a punctured left neighborhood of `0`, the condition `x < 0` is true and the `Piecewise` value is `0`. The limit from the left is therefore `0`, not the default branch value.

## Suggested regression test

Add `pr/tests/test_bug_006_left_hand_limit_of_piecewise_jump_returns_right_branch.py`, which checks the representative jump and five additional constant-branch jumps.
