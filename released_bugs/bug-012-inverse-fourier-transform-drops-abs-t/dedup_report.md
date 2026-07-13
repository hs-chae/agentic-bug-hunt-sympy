---
verdict: family_known_specific_new
confidence: 78
---

## Candidate Summary

`inverse_fourier_transform(2/(1 + 4*pi**2*w**2), w, t)` returns `exp(-t)` in SymPy 1.14.0. With SymPy's Fourier convention this transform pair should invert to `exp(-Abs(t))`, so the returned expression is wrong for negative real `t`, e.g. at `t = -1`.

## Search Queries

- `SymPy inverse_fourier_transform 2/(1+4*pi**2*w**2) exp(-t) exp(-Abs(t))`
- `site:github.com/sympy/sympy inverse_fourier_transform exp(-Abs(t)) Lorentzian`
- `"inverse_fourier_transform" "2/(1 + 4*pi**2*w**2)" SymPy`
- `"inverse_fourier_transform" "exp(-t)" "Abs(t)" SymPy`
- `github sympy issues Fourier transform exp(-Abs(t)) inverse_fourier_transform Lorentzian`
- `SymPy issue inverse Fourier transform conditions Piecewise`

## Closest Matches

- SymPy's transform documentation/source exposes `fourier_transform` and `inverse_fourier_transform`, but I found no public issue, PR, release-note entry, Stack Overflow post, or mailing-list thread describing this *specific* Lorentzian inverse returning `exp(-t)` instead of `exp(-Abs(t))`.
- However, the same *failure family* is documented in open/closed public issues in the exact function root_cause.md names:
  - https://github.com/sympy/sympy/issues/22787 (OPEN, "Bug in fourier_transform") — `_fourier_transform`/`fourier_transform` returns a non-even result for a real, even input, using the identical evenness argument F(k)=F(-k); still reproduces on 1.14.0. Same `_fourier_transform` Piecewise-branch failure family.
  - https://github.com/sympy/sympy/issues/14624 (CLOSED, "Inverse Fourier transform of a partial fraction decomposition looks to give a wrong answer") — `inverse_fourier_transform` returning a result that is wrong on the t<0 half-line.
- General web results included unrelated Fourier-transform material, such as a q-generalized inverse Fourier transform paper, but not a SymPy bug report for this expression.
- Local SymPy tests include Fourier transform coverage, but no test or public reference for `2/(1 + 4*pi**2*w**2)` or the missing absolute value in its inverse.

## Similarity Analysis

The closest material is only subsystem-level: public SymPy documentation and tests show that Fourier transforms are supported, and external search results discuss Fourier transforms generally. None of the matches names the rational Lorentzian transform, the output `exp(-t)`, the expected `exp(-Abs(t))`, or a negative-`t` counterexample.

## Specific Novelty Assessment

Under the duplicate criterion, no public report describes this exact Lorentzian inverse-transform counterexample, so the concrete instance is new. But the underlying defect is not novel: the `_fourier_transform` Piecewise-branch failure that yields a non-even, half-line-only result for a real even input is a documented, still-open issue (#22787), with a closely related closed report (#14624) on `inverse_fourier_transform` being wrong for t<0. The correct verdict is therefore `family_known_specific_new` — a new concrete instance of a known open Fourier-transform/Piecewise-branch failure family, not a novel bug.

## Recommendation

continue_to_artifact_generation
