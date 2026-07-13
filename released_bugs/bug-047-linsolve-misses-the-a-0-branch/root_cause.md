---
diagnosis_status: narrowed
confidence: 86
location: sympy/polys/matrices/linsolve.py:123
---

## Candidate Summary

`linsolve([a*x - a], [x])` returns `{(1,)}`. This misses the branch `a = 0`, where the equation becomes `0 = 0` and every `x` is a solution.

## Call Path

The public call is `linsolve([a*x - a], [x])`.

`linsolve` recognizes a list of equations and calls `_linsolve(eqs, symbols)` at `sympy/solvers/solveset.py:3105-3108`. That internal solver is imported from `sympy.polys.matrices.linsolve`.

In `sympy/polys/matrices/linsolve.py`, `_linsolve` converts the input equations to coefficient dictionaries at line 75, builds a sparse augmented matrix with `sympy_dict_to_dm` at line 76, and computes its RREF with `sdm_irref(Aaug)` at line 86.

For the reproducer, `_linear_eq_to_dict([a*x - a], [x])` gives coefficient `{x: a}` and constant `-a`. `sympy_dict_to_dm` constructs the domain at line 123 with `construct_domain(elems, field=True, extension=True)`, producing `ZZ(a)`, the rational-function field in `a`. The augmented row is `{0: {0: a, 1: a}}`.

## Root Cause

The root cause is the generic-field treatment of symbolic parameters in the sparse linear solver. The relevant steps are `sympy/polys/matrices/linsolve.py:120-136` and line 86:

```python
K, elems_K = construct_domain(elems, field=True, extension=True)
...
Arref, pivots, nzcols = sdm_irref(Aaug)
```

For this reproducer the constructed domain is `ZZ(a)`. In that field, the element `a` is nonzero/invertible unless it is the zero rational function. RREF therefore divides the row `[a, a]` by `a` and obtains `[1, 1]`, yielding `x = 1`. No parameter condition `a != 0` is returned, and no branch is created for the specialization `a = 0`.

I mark this as narrowed because the faulty behavior is a design choice of the linear-solver domain/RREF pipeline rather than a small arithmetic typo: parameters outside the solve-symbol list are treated as generic coefficient-field elements.

## Mechanism

The equation is `a*(x - 1) = 0`. Over the rational-function field `ZZ(a)`, `a` is invertible, so the solver is solving the generic case `a != 0`. Row reduction divides by the pivot `a` and returns `x = 1`.

After substitution `a = 0`, however, the original equation has no constraint on `x`. The returned finite set has no representation of the omitted `a = 0` branch, so values such as `x = 2` are incorrectly absent after specializing `a` to zero.

## Suggested Fix Direction

For systems with symbolic coefficients, `linsolve` should either document/return only generic solutions or carry pivot nonzero conditions and split degenerate parameter branches. In this case it would need to return something conditional: `x = 1` when `a != 0`, and all `x` when `a = 0`.

## Confidence and Caveats

Confidence is high that the missing branch comes from treating `a` as an invertible coefficient-field element during RREF. The caveat is that SymPy has multiple linear-solver implementations; I traced the public result and the equivalent polys RREF mechanism, but did not fully step through every line of the sparse `_linsolve` wrapper.
