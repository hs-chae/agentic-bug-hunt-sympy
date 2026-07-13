---
verdict: novel
confidence: 84
---

## Candidate Summary

`density(given(U, U > S.Half))(x)` for `U = Uniform("U", 0, 1)` returns a density equal to `2` on the original support `[0, 1]`. The expected conditional density is `2` only on `[1/2, 1]`; the returned density integrates to `2` and gives positive mass below the conditioning threshold.

## Search Queries

- `SymPy density given Uniform condition support conditional density wrong support`
- `site:github.com/sympy/sympy given Uniform density conditional_space support density`
- `"density(given" "Uniform" "1/2" SymPy`
- `"ConditionalContinuousDomain" "density" SymPy`
- `"density(given(Uniform"`
- `"ConditionalContinuousDomain" "conditional_space"`
- `"density" "given" "Uniform" "sympy.stats"`
- `"given(U" "U >" "Uniform" "SymPy"`

## Closest Matches

- SymPy stats documentation for `density`/`given`: https://docs.sympy.org/latest/modules/stats.html. The docs describe conditional density APIs and show a discrete `given(X, X > 3)` example whose density support is restricted to the condition.
- General probability references, e.g. conditional probability distribution: https://en.wikipedia.org/wiki/Conditional_probability_distribution. These confirm the mathematical expectation that a conditional density is normalized on the conditioned event, but they are not SymPy bug reports.
- Public SymPy source for the relevant area exists in `sympy.stats`, but focused searches did not find an issue, PR, release note, Stack Overflow post, or mailing-list thread describing `density(given(Uniform(...), U > 1/2))` retaining the original support after normalization.

## Similarity Analysis

The documentation is close in API surface because it documents `density`, `given`, and conditional random variables. It does not describe this continuous `Uniform` support bug or any known limitation that conditional densities may retain the unconditional support.

The mathematical references are only background. They explain what the correct result should be, but they do not constitute a public SymPy report.

## Specific Novelty Assessment

I found no public report for the exact reproducer, the exact wrong output (`2*1_[0,1]` with total mass `2`), or the internal signature involving `ConditionalContinuousDomain` and `conditional_space`. A fix for a generic, hypothetical "conditional density should restrict support" issue would cover this, but I did not find such a public issue/PR/discussion.

## Recommendation

continue_to_artifact_generation
