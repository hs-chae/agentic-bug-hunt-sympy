import pytest
from sympy import S, pi, sin, sqrt, symbols
from sympy.calculus.util import continuous_domain


@pytest.mark.parametrize("k", [1, 2, 3, 4, 5, 6])
def test_continuous_domain_sqrt_sin_periodic_intervals(k):
    x = symbols("x")
    dom = continuous_domain(sqrt(sin(k*x)), x, S.Reals)
    assert dom.contains(5*pi/(2*k)) is S.true
