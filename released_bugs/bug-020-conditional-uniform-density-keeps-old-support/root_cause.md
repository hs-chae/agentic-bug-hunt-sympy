---
diagnosis_status: located
confidence: 94
location: sympy/stats/crv.py:446
---

## Candidate Summary

`density(given(U, U > 1/2))(x)` for `U = Uniform("U", 0, 1)` returns `2*Piecewise((1, (x >= 0) & (x <= 1)), (0, True))`. The normalizing factor for `P(U > 1/2)` is applied, but the support remains `[0, 1]` instead of being restricted to `(1/2, 1]`, so the density integrates to `2`.

## Call Path

The public call is `given(U, U > S.Half)` in `sympy.stats.rv.given`. It builds `fullspace = pspace(Tuple(expr, condition))`, calls `fullspace.conditional_space(condition)`, then swaps the original random symbol onto the returned conditional space.

For this univariate continuous case, the internal branch is:

`sympy.stats.rv.given` -> `sympy.stats.crv.ContinuousPSpace.conditional_space` -> `sympy.stats.rv.Density.doit` / `sympy.stats.rv.density` -> `sympy.stats.crv.ContinuousPSpace.compute_density`.

The trace script confirmed that `pspace(Y)` is a `ContinuousPSpace` whose domain is a `ConditionalContinuousDomain` with set `Interval.Lopen(1/2, 1)`, while its `pdf` is still the original uniform `Piecewise` divided by the conditioning normalizer.

## Root Cause

The responsible code is in `sympy/stats/crv.py`, especially `ContinuousPSpace.conditional_space` around lines 446-462 and `ContinuousPSpace.compute_density` around lines 333-340.

`conditional_space` creates `domain = ConditionalContinuousDomain(self.domain, condition)` and computes `norm = domain.compute_expectation(self.pdf, **kwargs)`, but then sets:

```python
pdf = self.pdf / norm.xreplace(replacement)
density = Lambda(tuple(domain.symbols), pdf)
return ContinuousPSpace(domain, density)
```

That density is only renormalized. It is not restricted by the conditional domain and does not include an indicator for the condition.

The second half of the fault is in `compute_density`: when the requested expression is the same random variable, it marginalizes only `randomsymbols = set(self.values) - {expr}`. In this reproducer that set is empty, so `self.domain.compute_expectation(self.pdf, symbols, **kwargs)` is called with no variables. `ConditionalContinuousDomain.compute_expectation` returns the expression unchanged when `variables` is empty, so the domain condition is never applied to the returned density.

## Mechanism

For `U ~ Uniform(0, 1)`, `conditional_space(U > 1/2)` correctly computes the conditional domain `(0 <= U) & (U <= 1) & (U > 1/2)` and normalizer `Integral(1_[0,1](_U), (_U, 1/2, 1)) = 1/2`.

It then constructs the conditional-space density as `1_[0,1](U) / (1/2)`, i.e. `2*1_[0,1](U)`. Because `density(Y)` asks for the density of the same variable, `compute_density` returns that lambda without integrating over `U` or intersecting with the conditional domain. The result is therefore `2` on all of `[0, 1]`, assigning mass below `1/2` and total mass `2`.

The probability path does not expose the same wrong support because `P(Y < 1/2)` uses `ContinuousPSpace.where`, which intersects the query condition with `self.domain.set`.

## Suggested Fix Direction

The conditional density should include the condition's support, not only the normalization. Possible fixes are to make `conditional_space` multiply the pdf by an indicator/Piecewise for `domain.as_boolean()`, or to make density extraction for a `ConditionalContinuousDomain` apply `domain.set` even when no variables are marginalized. The fix should avoid double-applying the original full-domain support already present in many distribution pdfs.

## Confidence and Caveats

Confidence is high because the traced conditional space has the correct restricted domain but an unrestricted renormalized pdf, and the source path explains exactly why no later step applies the condition for `density(Y)`. The caveat is that a general fix must account for multivariate conditional domains and conditions that cannot be converted cleanly to an interval.
