---
verdict: family_known_specific_new
confidence: 84
---

## Dedup Re-classification

A re-audit found open public issues the original search missed. They belong to
the same `rsolve_hyper`-returns-`0` failure family: `rsolve` silently returns
the zero sequence for variable-coefficient / higher-order recurrences, so it
returns `0` even before initial conditions are applied.

- https://github.com/sympy/sympy/issues/27902 — "rsolve: Gives 0 for higher
  order recurrences" (open). Most direct match: its example
  `rsolve(y(n+2) - n*y(n+1) - y(n), y(n))` returns `0`, the same second-order
  variable-coefficient `rsolve_hyper`-returns-`0` defect as bug-019's no-IC case.
- https://github.com/sympy/sympy/issues/17982 — "Wrong result from rsolve" (open).
- https://github.com/sympy/sympy/issues/11063 — "Some wrong answers from rsolve"
  (open).

The underlying defect (`rsolve_hyper` fails to find the solution family and
returns `0`) is publicly reported, most directly in #27902. Bug-019's
specific lens — the IC-validation block `if symbols and init is not None:` being
skipped for the constant-free `0` candidate, so supplied `y(0)=y(1)=1` are never
checked — is the new specific instance within that known family, hence
`family_known_specific_new` rather than `novel`.

## Candidate Summary

`rsolve(y(n+2) - (n+2)*y(n+1) + y(n), y(n), {y(0): 1, y(1): 1})` returns `0`, whose values at `n=0` and `n=1` are both `0`. The supplied initial conditions require both values to be `1`.

## Search Queries

- `SymPy rsolve initial conditions returns 0 violates initial conditions y(n+2) -(n+2)*y(n+1)+y(n)`
- `site:github.com/sympy/sympy rsolve initial conditions returns 0 recurrence y(n+2) (n+2) y(n+1)`
- `"rsolve" "initial conditions" "SymPy"`
- `"rsolve" "y(0)" "y(1)" "SymPy"`
- `sympy rsolve recurrence initial condition issue`
- `sympy rsolve returns wrong initial conditions`
- `site:stackoverflow.com sympy rsolve initial conditions`
- `site:groups.google.com/g/sympy rsolve initial conditions`

## Closest Matches

- SymPy's public `rsolve` documentation describes solving linear recurrences with rational coefficients and explicitly supports initial conditions as a dictionary or list: https://docs.sympy.org/latest/modules/solvers/solvers.html#sympy.solvers.recurr.rsolve
- The documented examples include applying initial conditions to a second-order recurrence, but not a failure mode where a constant-free solution is returned without checking the conditions.

The original search surfaced no public report for this exact recurrence or the
exact symptom `rsolve(..., {y(0): 1, y(1): 1}) -> 0`. The re-audit corrects
this: open issues #27902, #17982, and #11063 report the same underlying
`rsolve`-returns-`0` failure family (see Dedup Re-classification above), with
#27902 being the most direct match.

## Similarity Analysis

The public documentation confirms that the candidate is in a supported API surface and that initial conditions are intended to constrain the returned recurrence solution. It does not report this bug or any equivalent bug in which `rsolve` returns a solution that violates supplied initial conditions.

The searches for `rsolve` plus initial-condition and wrong-output terms did not produce a public report whose fix would automatically cover this variable-coefficient recurrence.

## Specific Novelty Assessment

The broader `rsolve`-returns-`0` failure is publicly known (#27902, #17982,
#11063). The specific path bug-019 documents — a constant-free candidate `0`
returned with empty `symbols`, so the `if symbols and init is not None:`
IC-validation block is skipped and supplied initial conditions are never checked
— is the new specific instance within that known family.

## Recommendation

continue_to_artifact_generation
