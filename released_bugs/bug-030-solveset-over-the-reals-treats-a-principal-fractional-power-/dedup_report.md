---
verdict: family_known_specific_new
confidence: 78
---

## Candidate Summary

`solveset(Eq((x**2)**Rational(1, 3), x**Rational(2, 3)), x, S.Reals)` returns `Reals` in SymPy 1.14.0. This includes negative inputs such as `x = -1`, where the principal-power sides differ.

## Search Queries

- `site:github.com/sympy/sympy "(x**2)**Rational(1, 3)"`
- `site:github.com/sympy/sympy "x**Rational(2, 3)" "solveset"`
- `"solveset(Eq((x**2)**Rational(1, 3), x**Rational(2, 3))"`
- `"(x**2)**Rational(1, 3)" "x**Rational(2, 3)"`
- `SymPy issue rational powers principal branch bug`
- `site:groups.google.com/g/sympy "fractional power" "principal branch"`

## Closest Matches

- SymPy `sqrt`/`cbrt` documentation: https://docs.sympy.org/latest/modules/functions/elementary.html#sympy.functions.elementary.miscellaneous.sqrt states that principal roots do not generally undo powers across branches, with examples for square roots and cube roots.
- SymPy `solveset` documentation: https://docs.sympy.org/latest/modules/solvers/solveset.html#sympy.solvers.solveset.solveset documents domain-sensitive solving.
- General CAS-family literature: https://arxiv.org/abs/1203.1350 discusses correctness hazards when simplifying fractional powers of powers.

## Similarity Analysis

The public documentation and literature cover the same broad mathematical issue: identities involving powers and rational exponents need branch conditions. They do not mention this exact equation, the real-domain `solveset` result `Reals`, or the negative-real counterexample for `x**(2/3)`.

An existing local artifact for `solveset(Eq((x**2)**Rational(1, 3), 1), x, S.Reals)` is related, but it is not public duplicate evidence and it has the opposite symptom of missing roots rather than accepting all reals.

## Specific Novelty Assessment

This is best classified as a known family with a specific new instantiation. A broad fix to principal rational-power solving might cover it, but no public report was found whose described resolution would automatically cover this exact reproducer.

## Recommendation

continue_to_artifact_generation
