import pytest
from sympy import Eq, I, S, solveset, symbols, tan

x = symbols("x")
CASES = [I, -I]

@pytest.mark.parametrize("target", CASES)
def test_tan_singular_targets_have_no_finite_complex_solution(target):
    assert solveset(Eq(tan(x), target), x, domain=S.Complexes) is S.EmptySet
