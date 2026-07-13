import pytest

from sympy import I, pi, simplify, sin, sinh


@pytest.mark.parametrize("offset", [1, 2, 3, 4, 5, 6])
def test_sinh_split_imaginary_period_preserves_remainder(offset):
    assert simplify(sinh(I*pi + I*(pi - offset)) + I*sin(offset)) == 0
