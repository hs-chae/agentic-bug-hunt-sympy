---
diagnosis_status: located
confidence: 94
location: sympy/solvers/solveset.py:4105
---

## Candidate Summary

`nonlinsolve([(x*y - x)/(x - 1) - y, y - 1], [x, y])` returns `{(1, 1)}` even though the first original equation is undefined at `x = 1`.

## Call Path

The public call enters `nonlinsolve` in `sympy/solvers/solveset.py`.

The relevant path is:

`nonlinsolve` (`solveset.py:3899`) -> `_separate_poly_nonpoly` (`solveset.py:3771`) -> `_simple_dens` records denominators (`solveset.py:3782-3783`) -> rational equations are converted to numerators (`solveset.py:3794-3796`) -> `_handle_poly` solves the resulting polynomial system (`solveset.py:3807`) -> early return when no equations remain (`solveset.py:4105-4108`).

## Root Cause

`_separate_poly_nonpoly` correctly records the original denominator `x - 1`:

```python
denominators.update(_simple_dens(eq, symbols))
```

but it then clears the rational equation by replacing the expression with only its numerator:

```python
eq = eq.as_numer_denom()[0]
poly = eq.as_poly(*symbols, extension=True)
```

For this reproducer, that turns the first equation into `-x + y`, and the second is `y - 1`.

The bug is in `nonlinsolve`'s zero-dimensional polynomial success path at `sympy/solvers/solveset.py:4105-4108`:

```python
if not remaining:
    # If there is nothing left to solve then return the solution from
    # solve_poly_system directly.
    return FiniteSet(*map(to_tuple, poly_sol))
```

This return bypasses the recorded `denominators`. Denominator exclusion is only passed to `substitution` in the `else` path at `solveset.py:4118`, so it is applied when there are remaining equations but not when `_handle_poly` solved everything.

## Mechanism

For the system:

```text
(x*y - x)/(x - 1) - y = 0
y - 1 = 0
```

`_separate_poly_nonpoly` records `{x - 1}` as an excluded denominator, but clears the first equation to `-x + y = 0`. `_handle_poly` solves the polynomial system `[-x + y, y - 1]` and gets `{x: 1, y: 1}`. Since `poly_eqs + nonpolys` is empty, `nonlinsolve` returns this tuple directly at `solveset.py:4105-4108`.

The point should have been rejected because `x - 1` is zero. Calling `substitution([-x + y, y - 1], [x, y], exclude={x - 1})` directly returns `EmptySet`, confirming that the exclusion machinery can reject the point when it is actually used.

## Suggested Fix Direction

Before the early return for `not remaining`, filter `poly_sol` against `denominators`, similar in spirit to `substitution`'s `_check_exclude`, or route zero-dimensional rational systems through the same denominator-aware validation path. The filter should reject a solution if any recorded denominator is zero under that solution.

## Confidence and Caveats

Confidence is high. The trace confirmed `_simple_dens` records `x - 1`, `_separate_poly_nonpoly` clears the equation to `-x + y`, direct `substitution(..., exclude={x - 1})` rejects the solution, and only the `not remaining` early return bypasses that exclusion.
