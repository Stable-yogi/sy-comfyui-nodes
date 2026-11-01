import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_content_shuffle as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def run():
    n = 0
    dx, dy = m.make_wobble_field(20, 30, 5, 0.5, 4)
    assert len(dx) == 20 and len(dy) == 20 and all(len(r) == 30 for r in dx + dy)
    n += 1
    assert (dx, dy) == m.make_wobble_field(20, 30, 5, 0.5, 4)
    n += 1
    assert dx != m.make_wobble_field(20, 30, 6, 0.5, 4)[0]
    n += 1
    zx, zy = m.make_wobble_field(12, 12, 3, 0.0, 8)
    assert all(v == 0.0 for r in zx + zy for v in r)
    n += 1
    limit = 0.5 * 0.25 * 20
    assert all(abs(v) <= limit + 1e-9 for r in dx + dy for v in r)
    assert any(abs(v) > 0 for r in dx for v in r)
    n += 2
    assert _raises(m.make_wobble_field, 10, 10, 0, 0.5, 1)
    assert _raises(m.make_wobble_field, 10, 10, 0, 0.5, 65)
    assert _raises(m.make_wobble_field, 10, 10, 0, 1.5, 8)
    assert _raises(m.make_wobble_field, 10, 10, 0, -0.1, 8)
    n += 4
    one = m.make_wobble_field(1, 7, 1, 1.0, 2)
    assert len(one[0]) == 1 and len(one[0][0]) == 7
    n += 1
    assert m.grid_cells(10, 20, 8) == (8, 16)
    n += 1
    spec = m.SYContentShuffle.INPUT_TYPES()["required"]
    assert list(spec) == ["image", "seed", "strength", "scale"]
    assert m.SYContentShuffle.RETURN_TYPES == ("IMAGE",)
    n += 2
    return n
