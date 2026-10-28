import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_video_size_fit as m


def raises(*args):
    try:
        m.fit_size(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    f = m.fit_size
    # fits already: only rounding
    assert f(512, 512, 1.0, 64) == (512, 512); n += 1
    assert f(500, 500, 1.0, 64) == (512, 512); n += 1
    # never above budget across many cases
    cases = [(1920, 1080, 0.9, 32), (3840, 2160, 1.0, 16), (1000, 3000, 0.5, 8), (777, 555, 0.3, 32),
             (4096, 4096, 2.0, 64), (100, 5000, 0.25, 2), (1280, 720, 0.92, 32), (1, 1, 0.01, 1)]
    for w, h, mp, k in cases:
        nw, nh = f(w, h, mp, k)
        assert nw * nh <= mp * 1e6; n += 1
        assert nw % k == 0 and nh % k == 0 and nw >= k and nh >= k; n += 1
    # aspect is kept closely
    nw, nh = f(1920, 1080, 0.9, 32)
    assert abs(nw / nh - 1920 / 1080) < 0.08; n += 1
    assert (nw, nh) == f(1920, 1080, 0.9, 32); n += 1  # same input, same answer
    # a small picture is not enlarged
    assert f(256, 256, 4.0, 64) == (256, 256); n += 1
    # square wide
    nw, nh = f(4000, 1000, 0.5, 32)
    assert nw > nh * 3; n += 1
    # bad input
    assert raises(0, 100, 1.0, 32); n += 1
    assert raises(100, -1, 1.0, 32); n += 1
    assert raises(100, 100, 0, 32); n += 1
    assert raises(100, 100, 1.0, 0); n += 1
    assert raises(100, 100, 0.0005, 64); n += 1  # budget below one block
    assert m.SYVideoSizeFit().run(1920, 1080, 0.9, 32) == f(1920, 1080, 0.9, 32); n += 1
    return n
