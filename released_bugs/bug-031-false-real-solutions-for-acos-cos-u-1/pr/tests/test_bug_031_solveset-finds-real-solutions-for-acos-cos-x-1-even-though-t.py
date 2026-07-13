import pytest
from sympy import EmptySet, Eq, S, acos, cos, solveset, symbols

@pytest.mark.parametrize("a", [1, 2, 3, 4, 5, 6])
def test_solveset_acos_cos_negative_target_is_empty(a):
    u = symbols("u")
    assert solveset(Eq(acos(cos(u)), -a), u, S.Reals) == EmptySet
