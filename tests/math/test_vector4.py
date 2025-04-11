import math

import pytest

from spyke.math import Vector4


def test_vector4_dot():
    a = Vector4(1, 2, 3, 4)
    b = Vector4(2, 0, 1, 3)
    assert a.dot(b) == pytest.approx(17.0)

def test_vector4_length():
    v = Vector4(1, 2, 2, 1)
    assert v.length() == pytest.approx(math.sqrt(10))

def test_vector4_distance():
    a = Vector4(1, 1, 1, 1)
    b = Vector4(2, 2, 2, 2)
    assert a.distance(b) == pytest.approx(2.0)

def test_vector4_normalize():
    v = Vector4(2, 0, 0, 0)
    assert v.normalized().length() == pytest.approx(1.0)

def test_vector4_interpolate():
    a = Vector4(0, 0, 0, 0)
    b = Vector4(2, 4, 6, 8)
    c = a.interpolate(b, 0.5)
    assert (c.x, c.y, c.z, c.w) == pytest.approx((1, 2, 3, 4))

def test_vector4_add():
    assert Vector4(1, 2, 3, 4) + Vector4(4, 3, 2, 1) == Vector4(5, 5, 5, 5)

def test_vector4_sub():
    assert Vector4(1, 2, 3, 4) - Vector4(4, 3, 2, 1) == Vector4(-3, -1, 1, 3)

def test_vector4_mul():
    assert Vector4(1, 2, 3, 4) * 2 == Vector4(2, 4, 6, 8)

def test_vector4_div():
    assert Vector4(4, 3, 2, 1) / 2 == Vector4(2, 1.5, 1, 0.5)

def test_vector4_neg():
    assert -Vector4(1, 2, 3, 4) == Vector4(-1, -2, -3, -4)

def test_vector4_iadd():
    v = Vector4(1, 2, 3, 4)
    v += Vector4(1, 1, 1, 1)
    assert v == Vector4(2, 3, 4, 5)

def test_vector4_isub():
    v = Vector4(4, 5, 6, 7)
    v -= Vector4(1, 2, 3, 4)
    assert v == Vector4(3, 3, 3, 3)

def test_vector4_imul():
    v = Vector4(1, 2, 3, 4)
    v *= 2
    assert v == Vector4(2, 4, 6, 8)

def test_vector4_idiv():
    v = Vector4(4, 6, 8, 10)
    v /= 2
    assert v == Vector4(2, 3, 4, 5)

def test_vector4_mod_scalar():
    assert Vector4(5, 7, 9, 11) % 2 == Vector4(1, 1, 1, 1)

def test_vector4_mod_vector():
    assert Vector4(5, 7, 9, 11) % Vector4(2, 3, 4, 5) == Vector4(1, 1, 1, 1)

def test_vector4_imod_scalar():
    v = Vector4(5, 7, 9, 11)
    v %= 2
    assert v == Vector4(1, 1, 1, 1)

def test_vector4_imod_vector():
    v = Vector4(5, 7, 9, 11)
    v %= Vector4(2, 3, 4, 5)
    assert v == Vector4(1, 1, 1, 1)

def test_vector4_add_scalar():
    assert Vector4(1, 2, 3, 4) + 1 == Vector4(2, 3, 4, 5)

def test_vector4_sub_scalar():
    assert Vector4(5, 6, 7, 8) - 1 == Vector4(4, 5, 6, 7)

def test_vector4_mul_scalar():
    assert Vector4(1, 2, 3, 4) * 2 == Vector4(2, 4, 6, 8)

def test_vector4_div_scalar():
    assert Vector4(2, 4, 6, 8) / 2 == Vector4(1, 2, 3, 4)

def test_vector4_iadd_scalar():
    v = Vector4(1, 2, 3, 4)
    v += 1
    assert v == Vector4(2, 3, 4, 5)

def test_vector4_isub_scalar():
    v = Vector4(5, 6, 7, 8)
    v -= 1
    assert v == Vector4(4, 5, 6, 7)

def test_vector4_imul_scalar():
    v = Vector4(1, 2, 3, 4)
    v *= 2
    assert v == Vector4(2, 4, 6, 8)

def test_vector4_idiv_scalar():
    v = Vector4(2, 4, 6, 8)
    v /= 2
    assert v == Vector4(1, 2, 3, 4)

def test_vector4_div_by_zero():
    with pytest.raises(ZeroDivisionError):
        _ = Vector4(1, 2, 3, 4) / 0

def test_vector4_mod_by_zero():
    with pytest.raises(ZeroDivisionError):
        _ = Vector4(1, 2, 3, 4) % 0

def test_vector4_idiv_by_zero():
    v = Vector4(1, 2, 3, 4)
    with pytest.raises(ZeroDivisionError):
        v /= 0

def test_vector4_imod_by_zero():
    v = Vector4(1, 2, 3, 4)
    with pytest.raises(ZeroDivisionError):
        v %= 0

def test_vector4_float_constructor():
    v = Vector4(5.0)
    assert v == Vector4(5.0, 5.0, 5.0, 5.0)

def test_vector4_tuple_constructor():
    v = Vector4((1.0, 2.0, 3.0, 4.0))
    assert v == Vector4(1.0, 2.0, 3.0, 4.0)

def test_vector4_list_constructor():
    v = Vector4([1.0, 2.0, 3.0, 4.0])
    assert v == Vector4(1.0, 2.0, 3.0, 4.0)

def test_vector4_buffer_constructor():
    v = Vector4(b'\x00\x00\x80?\x00\x00\x00@\x00\x00@@\x00\x00\x80@')
    assert v == Vector4(1.0, 2.0, 3.0, 4.0)

def test_vector4_multi_value_constructor():
    v = Vector4(1.0, 2.0, 3.0, 4.0)
    assert v.x == 1.0 and v.y == 2.0 and v.z == 3.0 and v.w == 4.0

def test_vector4_zero():
    assert Vector4.zero() == Vector4(0.0, 0.0, 0.0, 0.0)

def test_vector4_one():
    assert Vector4.one() == Vector4(1.0, 1.0, 1.0, 1.0)

def test_vector4_unit_x():
    assert Vector4.unit_x() == Vector4(1.0, 0.0, 0.0, 0.0)

def test_vector4_unit_y():
    assert Vector4.unit_y() == Vector4(0.0, 1.0, 0.0, 0.0)

def test_vector4_unit_z():
    assert Vector4.unit_z() == Vector4(0.0, 0.0, 1.0, 0.0)

def test_vector4_unit_w():
    assert Vector4.unit_w() == Vector4(0.0, 0.0, 0.0, 1.0)
