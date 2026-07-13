import cmath
import pytest
from sympy import Eq, S, acos, acosh, asinh, atan, pi, I, solveset, symbols, simplify

x = symbols("x")
CASES = [("2*pi*I", 2*pi*I, 1, complex(0, 2*cmath.pi)), ("-2*pi*I", -2*pi*I, 1, complex(0, -2*cmath.pi)), ("3*pi*I", 3*pi*I, -1, complex(0, 3*cmath.pi)), ("-3*pi*I", -3*pi*I, -1, complex(0, -3*cmath.pi)), ("4*pi*I", 4*pi*I, 1, complex(0, 4*cmath.pi)), ("-4*pi*I", -4*pi*I, 1, complex(0, -4*cmath.pi))]

@pytest.mark.parametrize("label,target,bad,_target_complex", CASES)
def test_bug_027_solveset_returns_1_for_acosh_x_2_pi_i_outside_the_principal_(label, target, bad, _target_complex):
    func = acosh
    sol = solveset(Eq(func(x), target), x, domain=S.Complexes)
    assert sol.contains(bad) is not S.true
    assert simplify(func(bad) - target) != 0
