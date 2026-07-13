---
verdict: duplicate_of_existing_pr
confidence: 90
note: This bug duplicates open (unmerged) PR #29424 (https://github.com/sympy/sympy/pull/29424), an existing public fix for the exact symptom and root cause, created 2026-03-16.
---

## Candidate Summary

`limit(polygamma(0, x), x, 0, dir="+")` returns `zoo`, but the digamma Laurent expansion at zero has leading term `-1/x`, so the right-hand limit should be `-oo`.

## Search Queries

- `"limit(polygamma(0, x), x, 0" SymPy`
- `"digamma" "zoo" "SymPy" "limit"`
- `"polygamma(0, x)" "zoo" "SymPy"`
- `site:github.com/sympy/sympy polygamma limit 0 zoo -oo digamma SymPy`
- GitHub issue search: `repo:sympy/sympy polygamma limit zero digamma`
- GitHub issue search: `repo:sympy/sympy "polygamma(0, x)" limit`

## Closest Matches

- https://github.com/sympy/sympy/issues/5415 reports an older open `limit` failure involving `polygamma`, but it is about a multi-argument-order expression raising an exception as `x -> oo`, not a signed one-sided pole at zero.
- https://github.com/sympy/sympy/issues/5229#issuecomment-36998705 mentions making limit code work with `polygamma(0, x)` for harmonic-number asymptotics. This is only a discussion comment and does not describe the zero-pole sign bug.
- https://github.com/sympy/sympy/pull/29424 (OPEN, created 2026-03-16, "functions: fix polygamma leading term at poles and Mul integer assumption") is an existing unmerged public fix for exactly this bug. Its before/after section shows `limit(polygamma(0, x), x, 0, '+')` returning `zoo` and being fixed to `-oo`, with the same root cause in `polygamma._eval_as_leading_term` (`gamma_functions.py`). This PR predates the bundle by ~3 months and makes the candidate a duplicate of an existing report+fix.
- https://docs.sympy.org/latest/modules/functions/special.html documents `digamma(0)`/`polygamma` behavior.

## Similarity Analysis

The public material shows that `polygamma` in limits is a known problem area. Issue 5415 and the issue 5229 comment are different failure modes. More importantly, open PR #29424 (https://github.com/sympy/sympy/pull/29424) is an exact match: same symptom (`limit(polygamma(0, x), x, 0, '+')` returning `zoo`), same expected result (`-oo`), and same root cause (`polygamma._eval_as_leading_term` in `gamma_functions.py` not exposing the pole leading term).

## Specific Novelty Assessment

This specific right-hand digamma pole limit IS publicly reported and fixed: open PR #29424 (https://github.com/sympy/sympy/pull/29424, created 2026-03-16, still unmerged) targets exactly `limit(polygamma(0, x), x, 0, '+') -> zoo` and the missing `-oo` sign, with the same root cause. The candidate is therefore a duplicate of an existing unmerged fix rather than a novel specific bug.

## Recommendation

continue_to_artifact_generation (noting this duplicates existing open PR #29424)
