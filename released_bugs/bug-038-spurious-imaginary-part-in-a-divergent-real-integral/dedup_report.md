---
verdict: family_known_specific_new
confidence: 77
---

## Candidate Summary

`integrate(1/Abs(x), (x, -1, 0))` returns `oo + I*pi` in SymPy 1.14.0. The real positive improper integral diverges to `oo`; the finite imaginary part is a spurious principal-log branch contribution.

## Search Queries

- `SymPy integrate 1/Abs(x) -1 0 oo I*pi`
- `site:github.com/sympy/sympy "1/Abs(x)" "I*pi"`
- `"integrate(1/Abs(x), (x, -1, 0))"`
- `"oo + I*pi" "Abs(x)" "SymPy"`
- `SymPy issue definite integral Abs imaginary part I*pi`
- `Stack Overflow SymPy integrate Abs(x) I*pi`

## Closest Matches

- Open issue **sympy/sympy#23337**, "Spurious I*pi in improper definite integral" (created 2022-04-08, still open): <https://github.com/sympy/sympy/issues/23337>. This is a direct match for the same failure mode and the same root cause. It reports `integrate(1/(x-3), (x, 1, 3)) == -oo - I*pi`, where the logarithmic antiderivative `log(x-3)` evaluates to `log(2) + I*pi` at the finite endpoint via the principal complex log, and the `I*pi` branch constant fails to cancel during definite interval evaluation — exactly the `C = self.subs(x, c)` mechanism in `root_cause.md`. The `1/Abs(x)` case in this bundle is a specific new instantiation of #23337's already-reported defect.
- SymPy's public tests cover basic `Abs` behavior and integration of `Abs(t)`-like expressions, but no test pins down this divergent negative-side improper integral.

## Similarity Analysis

The closest family is improper real integration evaluated through logarithmic antiderivatives across a branch cut, and the matching public report is open issue #23337. The candidate's defining details are the real `Abs` integrand, the interval `[-1, 0]`, divergence to positive infinity, and the added `I*pi`. The integrand differs from #23337 (`1/Abs(x)` vs `1/(x-3)`), but the underlying defect — a spurious `I*pi` from a logarithmic antiderivative's principal-log branch constant during definite interval evaluation — is identical and already publicly reported in #23337.

## Specific Novelty Assessment

This should be treated as a specific new instance of an already-reported defect. The exact `integrate(1/Abs(x), (x, -1, 0))` reproducer does not appear verbatim in #23337, but it shares the root cause, so it is best cross-referenced against #23337 rather than filed as fully novel. A general fix for #23337's branch-cut handling in definite integration would likely cover this `Abs` case too.

## Recommendation

continue_to_artifact_generation
