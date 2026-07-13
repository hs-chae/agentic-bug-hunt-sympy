---
verdict: family_known_specific_new
confidence: 78
---

## Candidate Summary

`series((x**3)**Rational(1, 3), x, -1, 2)` returns `x`, but the principal cube root near negative real `x` is complex, not the real value `x`.

## Search Queries

- `"series((x**3)**(1/3), x, -1"`
- `"(x**3)**Rational(1, 3)" "series" "SymPy"`
- `"(x**3)**(1/3)" "principal" "series" "SymPy"`
- `site:github.com/sympy/sympy "Pow._eval_nseries" "branch"`
- GitHub issue search: `repo:sympy/sympy nseries pow branch cut principal root`
- GitHub issue search: `repo:sympy/sympy "wrong series" "Rational(1, 3)" "branch"`

## Closest Matches

- https://groups.google.com/g/sympy-issues/c/w-hWfr8Odz4 is an old imported issue titled `wrong series returned: sin(x**3)**Rational(1,3)`. It concerns a root inside a series expansion around zero, not a principal-branch expansion around `x = -1`.
- https://github.com/sympy/sympy/issues/23625 is documentation work for custom series methods and notes that branch cuts make series methods complicated.
- https://github.com/sympy/sympy/issues/9173 is a broad old series/limit issue, but it is not about principal powers or negative-real branch behavior.

## Similarity Analysis

Series expansion of rational powers and branch-sensitive functions is a known fragile area. The public matches do not describe this expression, this expansion point, or the incorrect denesting of `(x**3)**(1/3)` to `x` on the principal branch.

## Specific Novelty Assessment

I found no public report of `series((x**3)**Rational(1, 3), x, -1, 2)` returning `x`. A fix for the older `sin(x**3)**Rational(1,3)` series issue or the documentation issue would not automatically cover this negative-real principal-branch case.

## Recommendation

continue_to_artifact_generation
