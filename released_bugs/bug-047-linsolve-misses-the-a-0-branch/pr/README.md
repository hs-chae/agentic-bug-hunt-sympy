# Fix linsolve misses the a = 0 branch of a*x - a = 0

## Summary

This adds a regression test for a SymPy 1.14.0 correctness bug in `solvers.solveset / linear systems with symbolic parameters`.

## Reproducer

```python
x, a = symbols("x a")
sol = linsolve([a*x - a], [x])
print("solution:", sol)
print("equation at a=0, x=2:", (a*x - a).subs({a: 0, x: 2}))
print("reported contains x=2 after a=0:", (S(2),) in sol.subs(a, 0))
```

Current output:

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solution: {(1,)}
equation at a=0, x=2: 0
reported contains x=2 after a=0: False
```

## Expected behavior

A conditional solution: x = 1 when a != 0, and all x when a = 0.

## Evidence

The equation is a*(x - 1) = 0. If a != 0 then x = 1, but if a = 0 the equation becomes 0 = 0 and every x is a solution. The accompanying artifact `related_bugs.py` also checks five additional instantiations and an independent numerical or definition-based oracle.

## Suggested regression test

Add `pr/tests/test_bug_047_linsolve-misses-the-a-0-branch-of-a-x-a-0.py` or adapt its parametrized test into the relevant SymPy test module.
