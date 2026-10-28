import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_vram_estimate as m


def run():
    n = 0
    gb, text = m.estimate_vram(10, 1.5)
    assert abs(gb - 15.0) < 1e-9
    assert "estimate" in text.lower() and "15.0 GB" in text
    n += 2
    for bad in ((0, 1.3), (-1, 1.3), (5, 0.5)):
        try:
            m.estimate_vram(*bad)
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    out = m.SYVramEstimate().run(6.0, 1.3)
    assert abs(out[1] - 7.8) < 1e-9
    n += 1
    return n
