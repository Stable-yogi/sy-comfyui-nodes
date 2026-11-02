import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_dither as m


def _refuses(fn, word):
    try:
        fn()
    except ValueError as e:
        assert word in str(e), str(e)
        return 1
    raise SystemExit("expected ValueError")


def run():
    n = 0
    # normal: the known 4x4 Bayer pattern
    b4 = m.bayer_matrix(4)
    assert b4[0] == [0, 8, 2, 10] and b4[1] == [12, 4, 14, 6] and b4[3] == [15, 7, 13, 5]
    n += 3
    # every value used exactly once
    for size in (4, 8):
        flat = sorted(v for row in m.bayer_matrix(size) for v in row)
        assert flat == list(range(size * size)) and len(m.bayer_matrix(size)) == size
        n += 1
    # the 8x8 is built from the 4x4 (top-left block is 4x the 4x4)
    b8 = m.bayer_matrix(8)
    assert b8[0][:4] == [0, 32, 8, 40] and b8[0][4:] == [2, 34, 10, 42]
    n += 2
    # quantise: ends stay, middle snaps to the nearest step
    assert m.quantise(0.0, 4) == 0.0 and m.quantise(1.0, 4) == 1.0
    assert abs(m.quantise(0.4, 4) - 1.0 / 3.0) < 1e-12 and abs(m.quantise(0.6, 4) - 2.0 / 3.0) < 1e-12
    assert m.quantise(0.5, 2) == 1.0 and m.quantise(0.49, 2) == 0.0
    n += 3
    # edge: values outside 0..1 are clamped, 16 levels is allowed
    assert m.quantise(-3.0, 8) == 0.0 and m.quantise(9.0, 8) == 1.0 and m.quantise(1.0, 16) == 1.0
    n += 3
    # method check
    assert m.check_method("ordered 4x4", 99999) == "ordered 4x4" and m.check_method("floyd-steinberg", 1024) == "floyd-steinberg"
    n += 2
    # refusals
    n += _refuses(lambda: m.bayer_matrix(5), "4 or 8")
    n += _refuses(lambda: m.quantise(0.5, 1), "levels")
    n += _refuses(lambda: m.quantise(0.5, 17), "levels")
    n += _refuses(lambda: m.quantise(0.5, 2.5), "levels")
    n += _refuses(lambda: m.check_method("blue noise", 10), "method")
    n += _refuses(lambda: m.check_method("floyd-steinberg", 5000), "too wide for error diffusion")
    n += _refuses(lambda: m.dither_tensor(None, "ordered 8x8", 4, False, 1.5), "strength")
    d = m.SYDither.INPUT_TYPES()["required"]
    assert d["method"][1]["default"] == "ordered 8x8" and d["levels"][1]["default"] == 4 and d["strength"][1]["default"] == 1.0
    n += 1
    return n
