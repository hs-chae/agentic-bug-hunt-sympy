---
diagnosis_status: located
confidence: 90
location: sympy/calculus/singularities.py:95
---

## Candidate Summary

`singularities(polylog(1, x), x, S.Complexes)` returns `EmptySet`, but `polylog(1, x) = -log(1 - x)` has a logarithmic singularity at `x = 1`.

## Call Path

Public call: `singularities(expr, x, S.Complexes)` in `sympy/calculus/singularities.py`.

The function rewrites trigonometric/hyperbolic functions, scans `Pow` atoms with negative exponents, then scans the original expression for `log`, `asech`, `acsch`, `atanh`, and `acoth` atoms.

## Root Cause

The relevant code is `sympy/calculus/singularities.py`, lines 95-108. It only handles a small hard-coded set of forms:

```python
e = expression.rewrite([sec, csc, cot, tan], cos)
e = e.rewrite([sech, csch, coth, tanh], cosh)
for i in e.atoms(Pow):
    ...
for i in expression.atoms(log, asech, acsch):
    sings += solveset(i.args[0], symbol, domain)
for i in expression.atoms(atanh, acoth):
    ...
```

There is no `polylog` handling and no expansion through `expand_func`. `polylog._eval_expand_func` in `sympy/functions/special/zeta_functions.py`, lines 342-345, already knows that `polylog(1, z)` expands to `-log(1 - z)`, but `singularities` never asks for that rewrite.

## Mechanism

For `polylog(1, x)`, the expression has no `Pow` atoms and no `log` atoms. The hard-coded scans therefore add nothing and return the initial `EmptySet`.

If the expression is first expanded with `expand_func`, it becomes `-log(1 - x)`. The existing log branch then solves `1 - x = 0` and returns `{1}`. This shows the miss is in the singularity dispatch/rewriting, not in `solveset` for the log argument.

## Suggested Fix Direction

Add a special case for `polylog(1, z)` in `singularities`, or expand supported special functions before scanning for known singular forms. A narrower fix would detect `polylog` with first argument `1` and include the zeros of `1 - z`.

## Confidence and Caveats

Confidence is high for the `s = 1` reproducer. Broader polylog branch points may need a more general design, but the exact missed singularity at `x = 1` is caused by the missing expansion/handler described above.
