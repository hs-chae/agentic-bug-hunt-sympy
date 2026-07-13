---
verdict: family_known_specific_new
confidence: 77
---

## Candidate Summary

`summation((-1)**k*k*binomial(n, k), (k, 0, n))` returns `0` for nonnegative integer `n`, but direct evaluation at `n = 1` is `-1`. The generic Gosper certificate has a pole at `n = 1`, and the exceptional branch is lost.

## Search Queries

- `"summation((-1)**k*k*binomial(n, k)"`
- `site:github.com/sympy/sympy/issues summation (-1)**k*k*binomial(n,k) n=1`
- `site:github.com/sympy/sympy/issues Gosper binomial alternating n=1 exception`
- `"gosper_sum" "SymPy" "Piecewise"`
- `Stack Overflow SymPy summation alternating binomial wrong`

## Closest Matches

- [SymPy concrete/Gosper documentation](https://docs.sympy.org/latest/modules/concrete.html) documents `gosper_term` and `gosper_sum` as hypergeometric summation algorithms.
- [Gosper's algorithm](https://en.wikipedia.org/wiki/Gosper%27s_algorithm) gives general background on hypergeometric summation.
- [sympy/sympy#29731](https://github.com/sympy/sympy/issues/29731) — "A summation that evaluates to 0 even though it can be nonzero depending on the variable" (OPEN, created 2026-05-02, predating this bundle). Its reproducer `Sum(binomial(j,i)*(-1)**(j-i)*i**k,(i,0,j))` returns `0` but is nonzero at `j = 1`, and the issue diagnoses `gosper_sum` returning `0` because of a `(n-1)/(n-1) -> 1` cancellation that is invalid at the singular parameter value. This is the same `gosper_sum` lost-endpoint-exception failure family on essentially the same `(-1)`-weighted `i^k` binomial sum, with the same root cause as this candidate.

## Similarity Analysis

Public Gosper material is a family-level match because the root cause is a parameter-singular telescoping certificate. Beyond that, [sympy/sympy#29731](https://github.com/sympy/sympy/issues/29731) is a near-exact public report of this exact behavior: same `gosper_sum` subsystem, same loss of the singular endpoint exception (`n = 1`), and essentially the same `(-1)`-weighted `i^k` binomial summand. It is an open issue that predates this bundle, so this candidate is the same failure family rather than an unreported one.

## Specific Novelty Assessment

Known family: symbolic Gosper summation can depend on parameter conditions, and the specific `gosper_sum` lost-endpoint failure is already publicly reported in the open issue [sympy/sympy#29731](https://github.com/sympy/sympy/issues/29731). Specific behavior here: SymPy drops the `n = 1` exception for `sum((-1)**k*k*C(n,k), k=0..n)` — the same family as #29731, with this candidate adding the explicit `(-1)^k k C(n,k)` instantiation and the `k^p` (p=1..6) generalization.

## Recommendation

continue_to_artifact_generation
