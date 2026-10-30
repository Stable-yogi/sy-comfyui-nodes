import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_hue_shift as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def close(a, b, eps):
    return all(abs(x - y) < eps for x, y in zip(a, b))


IDENT = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def run():
    n = 0
    for deg in (0.0, 360.0):
        mat = m.hue_matrix(deg)
        assert all(close(mat[i], IDENT[i], 1e-3) for i in range(3)); n += 1
    inv = m.mat_mul(m.mat_inv(m.YIQ), m.YIQ)
    assert all(close(inv[i], IDENT[i], 1e-9) for i in range(3)); n += 1
    for deg in (-150.0, -30.0, 45.0, 120.0, 180.0):
        mat = m.hue_matrix(deg)
        for g in (0.0, 0.3, 0.5, 1.0):
            out = [sum(mat[i][j] * g for j in range(3)) for i in range(3)]
            assert close(out, (g, g, g), 2e-3); n += 1
    # rows of the matrix keep brightness (Y row sums unchanged: each row sums to 1)
    assert all(abs(sum(row) - 1.0) < 2e-3 for row in m.hue_matrix(77.0)); n += 1
    # three 120 degree shifts return to the start
    p = (0.55, 0.45, 0.35)
    q = p
    for _ in range(3):
        q = m.shift_pixel(q, 120.0, 1.0)
    assert close(q, p, 1e-2); n += 1
    # red turned by 120 is mostly green-ish / blue-ish, not red any more
    r = m.shift_pixel((1.0, 0.0, 0.0), 120.0, 1.0)
    assert r[0] < 0.5 and max(r[1], r[2]) > 0.5; n += 1
    # strength 0 keeps the pixel, 0.5 is halfway
    assert m.shift_pixel(p, 90.0, 0.0) == p; n += 1
    full = m.shift_pixel(p, 90.0, 1.0)
    half = m.shift_pixel(p, 90.0, 0.5)
    assert close(half, tuple((a + b) / 2 for a, b in zip(p, full)), 1e-9); n += 1
    # output stays in 0..1
    assert all(0.0 <= v <= 1.0 for v in m.shift_pixel((1.0, 1.0, 0.0), 77.0, 1.0)); n += 1
    # bad input
    assert raises(m.check_settings, 0.0, 2.0); n += 1
    assert raises(m.check_settings, 200.0, 1.0); n += 1
    assert raises(m.check_settings, -181.0, 1.0); n += 1
    assert raises(m.shift_pixel, p, 10.0, -0.1); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYHueShift"] == "Hue Shift SY"; n += 1
    return n
