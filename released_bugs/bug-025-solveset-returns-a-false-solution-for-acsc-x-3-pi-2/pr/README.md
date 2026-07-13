Title: Filter inverse acsc solveset candidates by principal range

Summary:

`solveset(Eq(acsc(x), 3*pi/2), x, S.Complexes)` returns `{-1}`, but `acsc(-1)` is `-pi/2`. The returned value has exact residual `-2*pi`.

Reproducer:

```python
from sympy import Eq, S, acsc, pi, simplify, solveset, symbols

x = symbols("x")
sol = solveset(Eq(acsc(x), 3*pi/2), x, S.Complexes)
print(sol)
print([simplify(acsc(candidate) - 3*pi/2) for candidate in sol])
```

Expected behavior:

`solveset` should not return values that fail substitution. Inverting an inverse trigonometric function by its forward function requires a principal-range check.

Evidence:

The proposed regression test checks the representative target and five related targets outside the principal `acsc` range.
