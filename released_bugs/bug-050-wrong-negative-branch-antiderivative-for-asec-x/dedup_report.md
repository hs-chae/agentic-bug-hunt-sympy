---
verdict: family_known_specific_new
confidence: 78
---

## Candidate Summary

The minimized reproducer computes `diff(integrate(asec(x), x), x) - asec(x)` for real `x` and evaluates it at `x = -2`. The residual is `-2*sqrt(3)/3`, so the antiderivative returned by `integrate(asec(x), x)` differentiates to the wrong value on the negative real branch.

## Search Queries

- `"integrate(asec(x), x)" SymPy wrong`
- `"diff(integrate(asec(x), x), x)" sympy`
- `"asec(x)" "integrate" "-2" "SymPy"`
- `SymPy integrate asec wrong negative x`
- `SymPy asec antiderivative wrong branch`
- `site:github.com/sympy/sympy "integrate(asec"`
- `site:github.com/sympy/sympy/issues "asec" "integrate"`
- `site:stackoverflow.com sympy asec integrate wrong`

## Closest Matches

- https://docs.sympy.org/latest/modules/integrals/integrals.html documents `integrate(f, x)` as returning an indefinite integral.
- https://docs.sympy.org/latest/modules/functions/elementary.html#sympy.functions.elementary.trigonometric.asec documents the branch behavior and special values of `asec`, including its branch cut and value at negative infinity.

No public issue, PR, Stack Overflow post, mailing-list discussion, or release-note entry was found for `integrate(asec(x), x)` producing an antiderivative with a nonzero derivative residual on negative real inputs. However, the broader family is well documented and the original "no public precedent" framing was overstated. The `integrate(asec(x), x)` capability under test was added by PR #19993 ("upgrades to manualintegrate", merged 2020-09-02, https://github.com/sympy/sympy/pull/19993), which closed issue #14329 ("Integration of asec and acsc", closed, https://github.com/sympy/sympy/issues/14329) and issue #19983 ("Sympy doesn't Integrate when expr contains asec / acsc", closed, https://github.com/sympy/sympy/issues/19983). Issue #14329 even shows the `Piecewise((acosh(x), Abs(x**2) > 1), ...)` shape; the buggy 1.14.0 output is the `real=True` variant of that primitive. The underlying wrong-real-branch Meijer/`acosh` mechanism ("output becomes worse when variables are declared real", `acosh` with an `Abs(...) > 1` split) is reported in the still-open issue #10453 ("integrate return wrong answer (inverse trigonometric functions).", open, https://github.com/sympy/sympy/issues/10453).

## Similarity Analysis

The official documentation confirms the intended API contract for indefinite integration and the branch-sensitive nature of `asec`, but it does not describe a known bug. Search results did not surface a public report involving `asec` integration, a residual at `x = -2`, or the exact residual `-2*sqrt(3)/3`.

This candidate is related to the general theme of branch correctness for inverse trigonometric functions, but the affected subsystem is integration rather than solving or singularity detection. The nearest public material is explanatory documentation, not a bug report or fix.

## Specific Novelty Assessment

This is a specific-new instance of a known family (`family_known_specific_new`). The asec antiderivative under test and its `Piecewise`/`acosh` shape are the feature of PR #19993 closing #14329 and #19983, and the same wrong-real-branch Meijer/`acosh` mechanism is reported in #10453, so the candidate belongs to a documented family rather than being fully novel. What remains unreported is the exact instance: a *nonzero derivative residual* (e.g. `-2*sqrt(3)/3` at `x = -2`) from `integrate(asec(x), x)` on the smooth negative real branch `x < -1`. No public material found describes that specific nonzero-residual instance or would automatically resolve it.

## Recommendation

continue_to_artifact_generation
