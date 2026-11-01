import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_upscale as m


def must_raise(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected a ValueError")


def run():
    n = 0
    T = m.TARGETS
    assert m.target_size(1000, 500, T[0], 0) == (1000, 500); n += 1
    assert m.target_size(1000, 500, T[1], 2000) == (2000, 1000); n += 1
    assert m.target_size(1000, 500, T[2], 1500) == (1500, 750); n += 1
    assert m.target_size(1000, 500, T[3], 1000) == (2000, 1000); n += 1
    assert m.target_size(1000, 1000, T[4], 4.0) == (2000, 2000); n += 1
    w, h = m.target_size(1001, 333, T[1], 777)
    assert w % 2 == 0 and h % 2 == 0 and abs(w - 777) <= 1; n += 1  # always even
    assert m.target_size(10, 1, T[1], 2) == (2, 2); n += 1  # never below 2
    assert "above 0" in must_raise(m.target_size, 100, 100, T[1], 0); n += 1
    assert "target" in must_raise(m.target_size, 100, 100, "Zoom", 5); n += 1
    assert "at least 1x1" in must_raise(m.target_size, 0, 100, T[1], 5); n += 1
    assert m.chunk_ranges(10, 4) == [(0, 4), (4, 8), (8, 10)]; n += 1
    assert m.chunk_ranges(3, 8) == [(0, 3)]; n += 1
    assert m.chunk_ranges(1, 1) == [(0, 1)]; n += 1
    assert "at least 1" in must_raise(m.chunk_ranges, 0, 4); n += 1
    t = m.info_text("4x.pth", (512, 512), (2048, 2048), (1024, 1024), 4, 2)
    assert "512x512 -> 1024x1024" in t and "model made 2048x2048" in t and "2 tries" in t; n += 1
    assert "plain resize" in m.info_text("None", (8, 8), (16, 16), (16, 16), 1, 1); n += 1
    assert m.SYUpscale.RETURN_NAMES == ("image", "info"); n += 1
    return n
