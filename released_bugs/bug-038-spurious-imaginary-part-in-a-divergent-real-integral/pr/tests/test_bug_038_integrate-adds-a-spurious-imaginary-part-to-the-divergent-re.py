import pytest
from sympy import Abs, integrate, oo, symbols


@pytest.mark.parametrize("a", [1, 2, 3, 4, 5, 6])
def test_improper_integral_abs_negative_side_has_no_imaginary_part(a):
    x = symbols("x", real=True)
    assert integrate(1/Abs(x), (x, -a, 0)) == oo
