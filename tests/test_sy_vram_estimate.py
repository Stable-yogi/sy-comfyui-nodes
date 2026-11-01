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
    # --- value pass A2: other models, card fit verdict
    gb, text = m.estimate_vram(10, 1.5, 4)
    assert abs(gb - 21.0) < 1e-9 and "10.0 GB file + 4.0 GB other models, x 1.50 overhead" in text; n += 2
    assert m.estimate_vram(10, 1.5, 0)[1] == m.estimate_vram(10, 1.5)[1]; n += 1
    try:
        m.estimate_vram(10, 1.5, -1)
        raise SystemExit("negative extra must raise")
    except ValueError:
        n += 1
    assert m.fit_verdict(15.0, 24) == (True, "Should fit: about 15.0 GB needed of 24 GB, 9.0 GB spare."); n += 1
    ok, t = m.fit_verdict(22.0, 24)
    assert ok is True and "tight" in t; n += 2
    ok, t = m.fit_verdict(30.0, 24)
    assert ok is False and t.startswith("Probably too big: about 30.0 GB needed but the card has 24 GB (6.0 GB short).") and "GGUF" in t; n += 2
    ok, t = m.fit_verdict(30.0, 0)
    assert ok is True and "not checked" in t; n += 2
    try:
        m.fit_verdict(1, -1)
        raise SystemExit("negative card must raise")
    except ValueError:
        n += 1
    out = m.SYVramEstimate().run(6.0, 1.3, 2.0, 8.0)
    assert len(out) == len(m.SYVramEstimate.RETURN_TYPES) == len(m.SYVramEstimate.RETURN_NAMES) == 4 and abs(out[1] - 10.4) < 1e-9 and out[2] is False; n += 1
    assert m.SYVramEstimate().run(6.0, 1.3)[2] is True; n += 1
    return n
