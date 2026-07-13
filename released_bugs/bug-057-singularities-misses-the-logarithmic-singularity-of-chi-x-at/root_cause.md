---
diagnosis_status: located
confidence: 88
location: sympy/calculus/singularities.py:97
---

## Candidate Summary

`singularities(Chi(x), x, S.Complexes)` returns `EmptySet`, although `Chi(0) = zoo` and the function has a logarithmic singularity at the origin.

## Call Path

Public call: `sympy.calculus.singularities.singularities`.

Concrete path:

`singularities` sympifies the expression, rewrites a small set of trigonometric and hyperbolic reciprocal functions, then scans for only a few syntactic singularity patterns: negative powers, `log`, `asech`, `acsch`, `atanh`, and `acoth` (`sympy/calculus/singularities.py:97-107`).

## Root Cause

The faulty limitation is in `sympy/calculus/singularities.py:97-107`: the algorithm never asks special functions for singular points and never inspects their leading terms. It only scans:

```python
for i in e.atoms(Pow): ...
for i in expression.atoms(log, asech, acsch): ...
for i in expression.atoms(atanh, acoth): ...
```

`Chi(x)` has no `Pow`, `log`, `asech`, `acsch`, `atanh`, or `acoth` atoms in this unevaluated form, so nothing is added to `sings`.

The singular information exists elsewhere: `Chi._atzero = S.ComplexInfinity` at `sympy/functions/special/error_functions.py:2286`, and `Chi._eval_as_leading_term` returns `log(x) + EulerGamma` near zero at `sympy/functions/special/error_functions.py:2307-2320`. `singularities` does not use either hook.

## Mechanism

For `Chi(x)`, the scans all find empty atom sets, so `sings` remains `S.EmptySet` and is returned. The code never checks `Chi(0)`, never rewrites to a form containing the logarithm, and never uses the implemented leading-term expansion that exposes the logarithmic singularity.

## Suggested Fix Direction

Add a special-function singularity hook or make `singularities` consult function-level information such as evaluation at candidate singular points or leading terms. For `Chi(arg)`, roots of `arg` should be included as logarithmic singularities.

## Confidence and Caveats

High confidence. The source path is straightforward: the current detector is syntactic and `Chi(x)` exposes no atoms that it knows how to collect.
