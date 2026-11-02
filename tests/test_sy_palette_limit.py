import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_palette_limit as m


def bad(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def run():
    n = 0
    dark, light = (0.1, 0.1, 0.1), (0.9, 0.9, 0.9)
    px = [dark] * 50 + [light] * 50
    p = m.kmeans_palette(px, 2, 0)
    assert len(p) == 2 and abs(p[0][0] - 0.1) < 1e-9 and abs(p[1][0] - 0.9) < 1e-9; n += 1  # darkest first
    px3 = [(0.0, 0.0, 0.0)] * 30 + [(1.0, 0.0, 0.0)] * 30 + [(0.0, 0.0, 1.0)] * 30
    p3 = m.kmeans_palette(px3, 3, 5)
    assert sorted(p3) == sorted([(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)]); n += 1
    assert m.kmeans_palette(px3, 3, 5) == p3; n += 1  # same seed, same answer
    big = [((i % 17) / 16.0, (i % 5) / 4.0, (i % 11) / 10.0) for i in range(20000)]
    a = m.kmeans_palette(big, 6, 1)
    assert len(a) == 6 and a == m.kmeans_palette(big, 6, 1); n += 1
    assert all(m.luma(a[i]) <= m.luma(a[i + 1]) for i in range(5)); n += 1
    one = m.kmeans_palette([(0.5, 0.5, 0.5)] * 10, 4, 0)
    assert len(one) == 4 and all(c == (0.5, 0.5, 0.5) for c in one); n += 1
    assert bad(m.kmeans_palette, px, 1, 0); n += 1
    assert bad(m.kmeans_palette, px, 65, 0); n += 1
    assert bad(m.kmeans_palette, [], 4, 0); n += 1
    assert m.palette_text([(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)]) == "#000000,#ffffff"; n += 1
    offs = [m.dither_offset(x, y, 1.0) for x in range(4) for y in range(4)]
    assert len(set(offs)) == 16 and min(offs) > -0.5 and max(offs) < 0.5; n += 1
    assert m.dither_offset(0, 0, 1.0) == m.dither_offset(4, 8, 1.0); n += 1
    assert m.dither_spread(64) < m.dither_spread(2) or m.dither_spread(64) == 0.5; n += 1
    assert m.SYPaletteLimit.RETURN_NAMES == ("image", "palette"); n += 1
    return n  # checks
