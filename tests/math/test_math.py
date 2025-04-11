import pytest

from spyke import math


def test_deg_to_rad():
    result = math.deg_to_rad(45.0)
    assert result == pytest.approx(0.7853981634)

def test_rad_to_deg():
    result = math.rad_to_deg(0.7853981634)
    assert result == pytest.approx(45.0)
