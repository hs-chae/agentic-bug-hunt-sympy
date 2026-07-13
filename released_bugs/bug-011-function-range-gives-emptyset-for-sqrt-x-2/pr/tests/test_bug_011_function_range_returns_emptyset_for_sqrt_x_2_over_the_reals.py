import pytest

from sympy import Interval, S, oo, sqrt, symbols
from sympy.calculus.util import function_range


@pytest.mark.parametrize("a", [0, 1, -1, 2, -2, 3])
def test_function_range_sqrt_shifted_square_over_reals(a):
    x = symbols("x")

    assert function_range(sqrt((x + a)**2), x, S.Reals) == Interval(0, oo)
