import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_gaussian_blur as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-6):
    return abs(a - b) < eps


def run():
    n = 0
    assert m.blur_line([0.1, 0.9, 0.3], 0) == [0.1, 0.9, 0.3]; n += 1
    k = m.gaussian_kernel(2.0)
    assert near(sum(k), 1.0) and len(k) == 13 and len(k) % 2 == 1; n += 1
    assert near(k[0], k[-1]) and k[6] == max(k); n += 1
    assert m.kernel_width(0) == 1; n += 1
    flat = m.blur_line([0.4] * 8, 2.0)
    assert all(near(a, 0.4) for a in flat); n += 1
    spike = m.blur_line([0.0] * 5 + [1.0] + [0.0] * 5, 1.0)
    assert spike[5] < 1.0 and spike[4] > 0.0 and near(spike[4], spike[6]); n += 1
    assert near(sum(spike), 1.0, 1e-4); n += 1
    assert raises(m.blur_line, [0.1], -0.5); n += 1
    return n
