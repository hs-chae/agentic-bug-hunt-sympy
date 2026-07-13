import pytest
from sympy import Mul, nan, pi, product, sin, symbols


@pytest.mark.parametrize("a", [1, 2, 3, 4, 5, 6])
def test_finite_product_preserves_undefined_factor_before_zero_collapse(a):
    n = symbols("n")
    term = sin(pi*n)/(n - a)
    values = [term.subs(n, i) for i in range(a - 1, a + 2)]

    assert nan in values
    assert Mul(*values) is nan
    assert product(term, (n, a - 1, a + 1)) is nan
