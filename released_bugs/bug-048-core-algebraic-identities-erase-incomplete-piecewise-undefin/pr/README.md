# Fix incomplete Piecewise undefined branches erased by core identities

## Summary

An incomplete `Piecewise`, such as `Piecewise((1, x > 0))`, is undefined outside its covered condition and SymPy evaluates it to `nan` at those points. Core algebraic simplifications currently erase that undefined region:

```python
from sympy import Eq, Piecewise, symbols

x = symbols("x", real=True)
p = Piecewise((1, x > 0))

print(p.subs(x, -1))
print((p*0).subs(x, -1))
print((p-p).subs(x, -1))
print(Eq(p, p).subs(x, -1))
```

Current output:

```text
nan
0
0
True
```

## Expected behavior

The undefined branch should remain observable, or these simplifications should be withheld when they would turn a partial expression into a total scalar or unconditional truth. At `x = -1`, the expression `p` is undefined, so `p*0`, `p-p`, and reflexive equality over `p` should not evaluate as ordinary finite identities there.

## Evidence

`Piecewise.eval` documents that a missing branch evaluates to `nan`. The proposed regression test covers the representative case plus five shifted instantiations of the same pattern. An independent Python `math.nan` oracle agrees that multiplication by zero, subtraction from itself, and equality are not ordinary finite operations on an undefined value.

## Suggested regression test

Add `test_bug_048_core_algebraic_identities_erase_incomplete_piecewise_undefin.py` under the appropriate SymPy test directory. It is parametrized over six incomplete `Piecewise` instances and currently fails on SymPy 1.14.0.
