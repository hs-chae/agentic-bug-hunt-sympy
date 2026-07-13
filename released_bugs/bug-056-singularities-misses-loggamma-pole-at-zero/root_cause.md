---
diagnosis_status: located
confidence: 88
location: sympy/calculus/singularities.py:103
---

## Candidate Summary

`singularities(loggamma(x), x, S.Complexes)` returns `EmptySet`, even though `loggamma(0)` evaluates to `oo` and `loggamma` is singular at the nonpositive integers.

## Call Path

The public call enters `sympy/calculus/singularities.py:singularities`. The expression is not rewritten into `log(gamma(x))`; it remains `loggamma(x)`. The structural scans for `Pow`, `log`, `atanh`, etc. find nothing relevant and return the initially empty set.

The probe showed:

```text
singularities: EmptySet
atoms Pow: set()
atoms log: set()
loggamma(0): oo
limit: oo
```

## Root Cause

The singularity detector in `sympy/calculus/singularities.py:94-108` is a limited structural detector. It handles negative powers, `log`, `asech`, `acsch`, `atanh`, and `acoth`, but it has no branch for `loggamma` or for special-function singularity metadata:

```python
for i in expression.atoms(log, asech, acsch):
    sings += solveset(i.args[0], symbol, domain)
...
return sings
```

Since `loggamma(x)` is neither an atom of `log` nor a `Pow`, the function returns `EmptySet`.

## Mechanism

`loggamma.eval` in `sympy/functions/special/gamma_functions.py:979-984` knows that nonpositive integer inputs evaluate to `oo`, but `singularities` never asks `loggamma` for such points and never rewrites it to `log(gamma(x))`. Therefore no equation such as `x = 0` or `x in nonpositive integers` is generated, and the initialized empty result is returned unchanged.

## Suggested Fix Direction

Add explicit singularity handling for `loggamma`, at least solving for nonpositive integer arguments. More generally, `singularities` could consult function-specific singularity hooks instead of relying only on a fixed list of elementary structural patterns.

## Confidence and Caveats

Confidence is high that this is the source-level reason for the empty result. The exact full singularity set over `S.Complexes` should be represented carefully, but the missing `0` follows directly from the absent `loggamma` handling.
