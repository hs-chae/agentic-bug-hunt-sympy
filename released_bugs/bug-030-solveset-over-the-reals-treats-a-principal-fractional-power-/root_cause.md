---
diagnosis_status: located
confidence: 88
location: sympy/solvers/solvers.py:3535
---

## Candidate Summary

`solveset(Eq((x**2)**Rational(1, 3), x**Rational(2, 3)), x, S.Reals)` returns `Reals`, but negative real values are false solutions for principal complex powers. At `x = -1`, the left side is `1` while the right side is the principal value `(-1)**(2/3)`.

## Call Path

The public call enters `sympy.solvers.solveset.solveset`, which normalizes the equality to `(x**2)**(1/3) - x**(2/3)` and calls `_solveset`. `_solveset` reaches the radical path and calls `sympy.solvers.solvers.unrad`, then `_solve_radical`.

The traced intermediate result is:

```text
unrad(-x**(2/3) + (x**2)**(1/3), x) -> (0, [])
solveset(0, x, S.Reals) -> Reals
```

## Root Cause

The specific faulty transformation is in `sympy/solvers/solvers.py:3535-3538`, in `unrad`'s two-radical-term case:

```python
eq = rterms[0]**lcm - (-rterms[1])**lcm
```

For this reproducer, `lcm` is `3`. Cubing both sides rewrites the equation as `x**2 - x**2`, so `unrad` returns the zero equation. That algebraic step assumes the principal-power identity `(x**2)**(1/3) == x**(2/3)` after cubing is reversible over the real solving domain. It is not reversible for negative real `x` because `x**(2/3)` is evaluated as a principal complex power.

As in candidate 044, `sympy/solvers/solveset.py:_solve_radical` only validates finite solution sets with `checksol`. The returned `Reals` set is not checked pointwise and is accepted.

## Mechanism

For `x = -1`, the two sides differ. However, after both sides are cubed they both become `1`, so the unradicalized equation is an identity. Solving that identity over `S.Reals` gives all real numbers, and the solver does not retain the branch restriction `x >= 0` needed for the principal-power equality.

## Suggested Fix Direction

`unrad` needs branch-condition awareness for rational powers, especially when raising both sides to an odd denominator power still hides principal complex-power choices. If it cannot produce those conditions, `_solve_radical` should return a conditional result rather than accepting a whole-domain superset.

## Confidence and Caveats

Confidence is high. The traced `unrad` output is exactly the zero equation that causes the global solution. The only caveat is fix ownership: robust correction may require both radical elimination and solveset result checking changes.
