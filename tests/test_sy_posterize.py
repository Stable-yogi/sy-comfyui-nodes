import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_posterize as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-9):
    return abs(a - b) < eps


def run():
    n = 0
    assert m.quantise(0.0, 2) == 0.0 and m.quantise(1.0, 2) == 1.0; n += 1
    assert m.quantise(0.4, 2) == 0.0 and m.quantise(0.6, 2) == 1.0; n += 1
    assert near(m.quantise(0.5, 3), 0.5); n += 1
    assert near(m.quantise(0.3, 4), 1 / 3.0) and near(m.quantise(0.7, 4), 2 / 3.0); n += 1
    assert m.quantise(1.0, 4) == 1.0 and m.quantise(0.0, 4) == 0.0; n += 1
    assert m.quantise(-0.5, 4) == 0.0 and m.quantise(2.0, 4) == 1.0; n += 1
    worst = max(abs(m.quantise(i / 1000.0, 256) - i / 1000.0) for i in range(1001))
    assert worst <= 1 / 255.0; n += 1
    assert all(m.quantise(i / 255.0, 256) == i / 255.0 or near(m.quantise(i / 255.0, 256), i / 255.0, 1e-9) for i in range(256)); n += 1
    outs = {m.quantise(i / 500.0, 5) for i in range(501)}
    assert outs == {0.0, 0.25, 0.5, 0.75, 1.0}; n += 1
    assert m.quantise(0.5, 2) == 1.0; n += 1  # halves round up
    # idempotent
    assert all(near(m.quantise(m.quantise(i / 97.0, 6), 6), m.quantise(i / 97.0, 6)) for i in range(98)); n += 1
    assert raises(m.quantise, 0.5, 1); n += 1
    assert raises(m.quantise, 0.5, 257); n += 1
    assert raises(m.check_levels, 0); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYPosterize"] == "Posterize SY"; n += 1
    return n
