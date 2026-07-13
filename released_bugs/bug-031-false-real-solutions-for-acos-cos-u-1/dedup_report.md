---
verdict: family_known_specific_new
confidence: 80
---

## Candidate Summary

Candidate 204 is a real-domain inverse-trigonometric composition error:

```python
u = symbols("u")
solveset(Eq(acos(cos(u)), -1), u, S.Reals)
```

SymPy 1.14.0 returns periodic real `ImageSet` families, including representatives such as `u = 1`, even though `acos(cos(u))` is always in `[0, pi]` for real `u` and therefore can never equal `-1`.

## Search Queries

- `SymPy solveset "acos(cos" "-1"`
- `"acos(cos(x))" "solveset" SymPy`
- `site:github.com/sympy/sympy "acos(cos" "solveset"`
- `SymPy solveset inverse trig composition acos cos branch`
- `"solveset" "incorrect solution" SymPy "acos"`
- `"SymPy" "_invert_real" "acos"`
- `Stack Overflow SymPy acos cos solveset`

## Closest Matches

No exact public SymPy issue, PR, Stack Overflow report, mailing-list discussion, or release-note entry was found for `solveset(Eq(acos(cos(u)), -1), u, S.Reals)` or for the reported periodic `ImageSet` output.

The closest public material is general inverse-trigonometric branch/range background, including Wikipedia's [Inverse trigonometric functions](https://en.wikipedia.org/wiki/Inverse_trigonometric_functions). That source discusses principal values and restricted inverse ranges, which is the same broad mathematical family, but it does not describe this SymPy solver result.

## Similarity Analysis

This candidate is caused by treating `acos` as globally invertible by applying `cos` to both sides, without first checking whether the target `-1` lies in the real principal range `[0, pi]`. The subsequent equation `cos(u) = cos(-1)` legitimately has real periodic solutions, but those solve only the transformed equation, not the original one.

General public material about inverse trig ranges is similar background. It is not a duplicate because resolving that material would not automatically patch SymPy's `solveset` inversion logic or remove the false `ImageSet` families.

## Specific Novelty Assessment

The broad inverse-trig principal-range family is known, but the exact `acos(cos(u)) = -1` `solveset` failure appears new. I found no public report whose resolution would necessarily cover this candidate.

## Recommendation

continue_to_artifact_generation
