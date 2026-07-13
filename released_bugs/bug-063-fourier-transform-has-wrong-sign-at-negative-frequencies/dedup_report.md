---
verdict: family_known_specific_new
confidence: 78
---

## Candidate Summary

For real `x, k`, `fourier_transform(cos(x)/(x**2 + 1), x, k)` gives the negative of the shift-theorem value at `k = -1/3`. The expected transform is positive and even:
`pi/2*(exp(-Abs(2*pi*k - 1)) + exp(-Abs(2*pi*k + 1)))`.

## Search Queries

- `"fourier_transform(cos(x)/(x**2 + 1)" SymPy`
- `"cos(x)/(x**2 + 1)" "fourier_transform" "SymPy"`
- `site:github.com/sympy/sympy fourier_transform cos(x)/(x**2+1) wrong sign negative k`
- `SymPy Fourier transform wrong sign negative frequencies Abs(k) meijerg`
- `"fourier_transform" "Abs(k)/k" "sympy"`
- `site:github.com/sympy/sympy/issues "fourier_transform" "wrong sign"`
- `Stack Overflow SymPy fourier_transform negative frequency wrong sign`
- `Stack Overflow sympy fourier transform abs k`

## Closest Matches

- SymPy 1.14.0 Fourier transform docs: https://docs.sympy.org/latest/modules/integrals/integrals.html#sympy.integrals.transforms.fourier_transform. The docs define the convention `Integral(f(x)*exp(-2*pi*I*x*k), (x, -oo, oo))` and note the default `noconds=True`.
- Public search results for the exact integrand, the wrong sign at negative `k`, `Abs(k)/k`, and related GitHub issue searches did not produce a matching public issue or discussion.

## Similarity Analysis

The official docs are relevant for the transform convention and condition handling, but they are not a bug report. The initial focused searches did not surface a public match for the exact integrand `fourier_transform(cos(x)/(x**2 + 1), x, k)`.

However, a follow-up audit identified an open public issue that the original search missed:

- sympy/sympy#25137 — "Integrate returns wrong answer for fourier transform of sinc" (OPEN; labels `integrals.transforms`, `integrals.meijerg`): https://github.com/sympy/sympy/issues/25137

This issue documents the same meijerg Fourier-transform `abs/k` sign family: with variables declared `real=True`, the meijerg path returns a wrong result carrying a spurious `Abs(k)/k`-type sign factor (correct when not real). A maintainer comment gives the exact root cause: "The meijerg integrator gets something like `y*sqrt(1/y**2)` which depending on the branch for `sqrt` can either be `1` or `sign(y) = abs(y)/y`." That is precisely the `Abs(k)/k` sign factor this bundle diagnoses.

## Specific Novelty Assessment

The "novel / no public precedent" framing is overstated. The underlying failure family — the meijerg Fourier-transform `abs/k` sign artifact under `real=True` — is a known, open issue (#25137), including a maintainer root-cause comment matching this diagnosis. The specific integrand `cos(x)/(x**2 + 1)` and its negative-frequency sign error are plausibly a new instance of that family, so this remains individually actionable as a reproducer and regression test, but it should be classified as a known family with a new specific instance, not novel.

## Recommendation

continue_to_artifact_generation
