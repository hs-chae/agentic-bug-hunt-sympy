---
diagnosis_status: located
confidence: 91
location: sympy/calculus/singularities.py:94
---

## Candidate Summary

`singularities(gamma(x), x, S.Complexes)` returns `EmptySet`, but `gamma` has poles at the nonpositive integers, including `x = 0`.

## Call Path

The public call enters `sympy/calculus/singularities.py::singularities`. The function sympifies `gamma(x)`, rewrites only trig/hyperbolic reciprocal forms, scans `Pow` atoms, then scans only `log`, `asech`, `acsch`, `atanh`, and `acoth` atoms before returning `sings`.

## Root Cause

The scanner in `sympy/calculus/singularities.py` lines 94-108 has no handling for `gamma` or general meromorphic special functions. For `gamma(x)`, the `Pow` and listed inverse/log atom scans are empty, so the initial `S.EmptySet` is returned unchanged.

`gamma.eval` does know that nonpositive integer numeric arguments evaluate to `ComplexInfinity` (`sympy/functions/special/gamma_functions.py:127-131`), but `singularities()` never uses that information. The class metadata also lists only `ComplexInfinity` in `_singularities` at `gamma_functions.py:112`, not the finite poles.

## Mechanism

Because `gamma(x)` is syntactically opaque to the singularities scanner, no equation such as `x in nonpositive integers` is generated. The function returns `EmptySet` even though substitution and the Laurent series show a simple pole at `0`.

## Suggested Fix Direction

Add a special-function singularity path for `gamma(g(x))`, solving for `g(x)` equal to nonpositive integers, or use richer function-level meromorphic singularity metadata.

## Confidence and Caveats

The scratch trace showed all scanner atom sets are empty for `gamma(x)`, and `singularities(gamma(x), x, S.Complexes)` returns the untouched initial `EmptySet`.
