import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_megapixel_scale as m


def _raises(*args):
    try:
        m.scale_to_megapixels(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    w, h = m.scale_to_megapixels(1024, 1024, 1.0, 16)
    assert w == h and w % 16 == 0 and abs(w * h - 1e6) / 1e6 < 0.04; n += 1
    w, h = m.scale_to_megapixels(2000, 2000, 1.0, 16)
    assert w % 16 == 0 and h % 16 == 0 and abs(w * h - 1e6) / 1e6 < 0.04; n += 1
    w, h = m.scale_to_megapixels(1920, 1080, 2.0, 16)
    assert w % 16 == 0 and h % 16 == 0 and abs(w / h - 16 / 9) < 0.03 and abs(w * h - 2e6) / 2e6 < 0.03; n += 1
    w, h = m.scale_to_megapixels(1080, 1920, 1.0, 64)
    assert w < h and w % 64 == 0 and h % 64 == 0; n += 1
    assert m.scale_to_megapixels(500, 500, 1.0, 1) == (1000, 1000); n += 1
    assert m.scale_to_megapixels(1, 1, 0.01, 1) == (100, 100); n += 1
    w, h = m.scale_to_megapixels(10000, 10, 0.01, 8)  # extreme aspect stays a valid multiple
    assert w % 8 == 0 and h % 8 == 0 and h >= 8; n += 1
    assert m.scale_to_megapixels(1024, 1024, 100.0, 16) == (10000, 10000); n += 1  # huge but legal
    for bad in ((0, 10, 1, 16), (10, 0, 1, 16), (10, 10, 0, 16), (10, 10, -1, 16), (10, 10, 1, 0),
                (10, 10, 5000, 16), (10, 10, float("nan"), 16), (10, 10, float("inf"), 16),
                (65536, 1, 4000, 1)):
        assert _raises(*bad), bad
        n += 1
    assert m.SYMegapixelScale().run(1024, 1024, 1.0, 1) == (1000, 1000); n += 1
    return n
