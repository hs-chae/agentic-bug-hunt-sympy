# Fix dsolve explicit branches for f' = sqrt(f**2)

## Summary

`dsolve(Eq(f'(x), sqrt(f(x)**2)))` returns both `C1*exp(-x)` and `C1*exp(x)`. With a positive constant, the decreasing branch has a nonzero ODE residual and is not a solution.

## Reproducer

```python
from sympy import *
x = symbols("x")
f = Function("f")
C1 = symbols("C1")
ode = Eq(diff(f(x), x), sqrt(f(x)**2))
sol = dsolve(ode)
rhs = sol[0].rhs.subs(C1, 1)
print(sol)
print(N((diff(rhs, x) - sqrt(rhs**2)).subs(x, 0), 50))
```

Current output:

```text
[Eq(f(x), C1*exp(-x)), Eq(f(x), C1*exp(x))]
-2.0000000000000000000000000000000000000000000000000
```

## Expected behavior

Every returned explicit branch should satisfy the ODE, or branches should include the necessary sign conditions.

## Evidence

The artifact `related_bugs.py` substitutes positive constants `1` through `6` into the returned branches and checks the ODE residual.

## Suggested regression test

Add `pr/tests/test_bug_007_dsolve_returns_a_solution_that_fails_f_sqrt_f_2.py`.
