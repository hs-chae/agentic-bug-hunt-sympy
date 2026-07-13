---
verdict: novel
confidence: 82
---

## Candidate Summary

`product(sin(pi*n)/(n - 1), (n, 0, 2))` returns `0`, even though the factor at `n = 1` is `nan`. The zero factors at `n = 0` and `n = 2` do not make a product containing an undefined factor well-defined.

## Search Queries

- `site:github.com/sympy/sympy/issues "product" "nan" "undefined" "factor"`
- `"product" "sin(pi*n)/(n - 1)" "github.com/sympy/sympy"`
- `"sin(pi*n)/(n - 1)" "SymPy"`
- `"product" "0/0" "SymPy" "github"`
- `SymPy product finite product undefined factor issue`
- `SymPy release notes summation nan product nan`

## Closest Matches

- SymPy concrete mathematics documentation for products: https://docs.sympy.org/latest/modules/concrete.html

No public issue, PR, Stack Overflow question, mailing-list thread, or release-note entry was found for this exact finite product or for the specific failure where integer-index assumptions simplify `sin(pi*n)` to zero before checking the denominator singularity.

## Similarity Analysis

This is related to a broad family of concrete-product domain bugs: simplification under index assumptions can mask undefined factors. The public material found does not identify this reproducer or a known fix whose scope would automatically force finite products to check original factors before collapsing an identically zero term.

## Specific Novelty Assessment

The minimized product appears publicly unreported. Because the found material is only general API/background documentation and not a concrete matching issue, the candidate should not be rejected as a duplicate.

## Recommendation

continue_to_artifact_generation
