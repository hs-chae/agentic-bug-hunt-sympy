---
diagnosis_status: located
confidence: 92
location: sympy/calculus/singularities.py:94
---

## Candidate Summary

`singularities(zeta(x), x, S.Complexes)` returns `EmptySet`, even though `zeta` has a simple pole at `x = 1`.

## Call Path

The public call enters `sympy.calculus.singularities.singularities`. It sympifies the expression, rewrites selected trig/hyperbolic functions, scans powers with negative exponents, and scans a small list of elementary functions (`log`, `asech`, `acsch`, `atanh`, `acoth`). No zeta-specific path is reached.

## Root Cause

`sympy/calculus/singularities.py:94-108` computes singularities only from:

- negative powers in `e.atoms(Pow)`;
- zeros of arguments to `log`, `asech`, and `acsch`;
- `+/-1` arguments to `atanh` and `acoth`.

Special functions such as `zeta` are not inspected, and unsupported functions do not trigger `NotImplementedError`; they simply contribute nothing to `sings`, so the function returns `EmptySet`.

The zeta class does know about the pole in `sympy/functions/special/zeta_functions.py:503-510`, where `zeta(1)` evaluates to `S.ComplexInfinity`, and its docstring states the simple pole at `s = 1`.

## Mechanism

For `zeta(x)`, the expression has no relevant negative `Pow` atom and no atoms of the listed elementary functions. The accumulator `sings` remains `S.EmptySet`, and line 108 returns it. The algorithm never asks whether `zeta(x)` is finite or meromorphic at candidate points and never uses the known `zeta(1) = zoo` behavior.

## Suggested Fix Direction

Add a special-function singularity hook or have `singularities` consult function metadata for known isolated poles. For `zeta(s)` and Hurwitz zeta with ordinary parameter values, solve `s - 1 = 0` and add that point to the singularity set. If no hook exists for an encountered special function, prefer `NotImplementedError` over silently returning an incomplete set.

## Confidence and Caveats

High confidence. The omission is visible in the complete `singularities` scan and is consistent with the reproducer output.
