import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_emboss as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def near(a, b, eps=1e-9):
    return abs(a - b) < eps


def run():
    n = 0
    assert m.emboss_kernel("top_left") == [[-2, -1, 0], [-1, 1, 1], [0, 1, 2]]; n += 1
    assert m.emboss_kernel("bottom_right") == [[2, 1, 0], [1, 1, -1], [0, -1, -2]]; n += 1
    for a in m.ANGLES:
        k = m.emboss_kernel(a)
        assert len(k) == 3 and all(len(r) == 3 for r in k); n += 1
        assert sum(sum(r) for r in k) == 1; n += 1
    assert len({str(m.emboss_kernel(a)) for a in m.ANGLES}) == 8; n += 1
    flat = [[0.3] * 4 for _ in range(3)]
    out = m.emboss_plane(flat, 5.0, "left")
    assert all(near(v, 0.5) for r in out for v in r); n += 1
    one = m.emboss_plane([[0.9]], 3.0, "top_left")
    assert near(one[0][0], 0.5); n += 1  # 1x1: replicate padding is flat
    ramp = [[0.0, 0.5, 1.0]] * 3
    out = m.emboss_plane(ramp, 0.1, "top_left")
    # centre: kernel rows give -0.5, 1.5 and 2.5, so conv = 3.5, minus luma 0.5 = 3.0, times 0.1 plus 0.5
    assert near(out[1][1], 0.8); n += 1
    out = m.emboss_plane(ramp, 1.0, "top_left")
    assert out[1][1] == 1.0; n += 1  # clamped
    out = m.emboss_plane([[0.0, 1.0]], 0.0, "top")
    assert out == [[0.5, 0.5]]; n += 1
    out = m.emboss_plane([[0.0, 1.0, 0.0, 1.0]] * 2, 10.0, "right")
    assert all(0.0 <= v <= 1.0 for r in out for v in r); n += 1
    msg = raises(m.emboss_kernel, "up")
    assert msg and "angle" in msg; n += 1
    msg = raises(m.emboss_plane, [[0.1]], 11.0, "top")
    assert msg and "strength" in msg; n += 1
    assert raises(m.emboss_plane, [], 1.0, "top"); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYEmboss"] == "Emboss SY"; n += 1
    assert m.SYEmboss.CATEGORY == "SY/Image"; n += 1
    return n
