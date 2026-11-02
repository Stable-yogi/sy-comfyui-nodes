import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_defocus_blur as m


def _refuses(fn, word, *args):
    try:
        fn(*args)
    except ValueError as e:
        assert word in str(e), str(e)
        return 1
    raise SystemExit("expected ValueError")


def run():
    n = 0
    # normal: whole-pixel disc, symmetric, centre included, area close to pi r^2
    pts = m.disc_offsets(5, "disc", 400)
    assert (0, 0) in pts and len(pts) == len(set(pts))
    assert all(dx * dx + dy * dy <= 25 for dx, dy in pts)
    assert abs(len(pts) - 3.14159 * 25) < 8
    assert all((-dx, -dy) in pts for dx, dy in pts)
    n += 4
    # hexagon sits inside its corner circle and is flatter at the top than the disc
    hx = m.disc_offsets(6, "hexagon", 400)
    assert all(dx * dx + dy * dy <= 36 for dx, dy in hx)
    assert max(dy for dx, dy in hx) == 5 and max(dx for dx, dy in hx) == 6
    n += 2
    # edge: tiny radius is one tap; the cap is kept for a huge radius, and the shape stays in the circle
    assert m.disc_offsets(0.4, "disc", 400) == [(0, 0)]
    big = m.disc_offsets(60, "disc", 400)
    assert 100 < len(big) <= 400 and all(dx * dx + dy * dy <= 61 * 61 for dx, dy in big)
    bigh = m.disc_offsets(60, "hexagon", 100)
    assert 20 < len(bigh) <= 100
    assert m.disc_offsets(50, "disc", 1)
    n += 4
    # highlight gain: dark stays 1, bright rises with boost, zero boost is flat
    assert m.highlight_gain(0.0, 1.0) == 1.0 and m.highlight_gain(1.0, 0.0) == 1.0
    assert m.highlight_gain(1.0, 1.0) == 16.0 and m.highlight_gain(0.9, 0.5) < m.highlight_gain(1.0, 0.5)
    n += 2
    # refusals
    n += _refuses(m.disc_offsets, "shape", 5, "star", 400)
    n += _refuses(m.disc_offsets, "radius", -1, "disc", 400)
    n += _refuses(m.disc_offsets, "max_taps", 5, "disc", 0)
    n += _refuses(m.highlight_gain, "boost", 0.5, 1.5)
    n += _refuses(m.highlight_gain, "luma", 1.5, 0.5)
    d = m.SYDefocusBlur.INPUT_TYPES()["required"]
    assert d["radius"][1]["default"] == 8.0 and d["shape"][1]["default"] == "disc" and d["highlight_boost"][1]["default"] == 0.3
    assert d["edge"][1]["default"] == "replicate"
    n += 1
    return n
