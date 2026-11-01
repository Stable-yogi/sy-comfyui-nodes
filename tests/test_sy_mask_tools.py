import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_tools as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-6):
    return abs(a - b) < eps


def block(h, w, x0, x1, y0, y1):
    return [[1.0 if x0 <= x < x1 and y0 <= y < y1 else 0.0 for x in range(w)] for y in range(h)]


def run():
    n = 0
    sq = block(12, 12, 4, 8, 4, 8)
    # neutral leaves the mask alone
    assert m.process(sq) == sq; n += 1
    # threshold
    assert m.process([[0.2, 0.5, 0.9]], threshold=0.5) == [[0.0, 1.0, 1.0]]; n += 1
    # invert last and first give the same for plain hard masks
    assert m.process(sq, invert=True) == [[1.0 - v for v in r] for r in sq]; n += 1
    assert m.process(sq, invert=True, invert_first=True) == [[1.0 - v for v in r] for r in sq]; n += 1
    # order: invert_first happens before the threshold, invert after it
    assert m.process([[0.2, 0.9]], threshold=0.5, invert_first=True) == [[1.0, 0.0]]; n += 1
    assert m.process([[0.2, 0.9]], threshold=0.5, invert=True) == [[1.0, 0.0]]; n += 1
    assert m.process([[0.4, 0.6]], threshold=0.5, invert=True) == [[1.0, 0.0]]; n += 1
    # grow and shrink
    assert sum(map(sum, m.process(sq, grow=1))) > sum(map(sum, sq)); n += 1
    assert sum(map(sum, m.process(sq, grow=-1))) < sum(map(sum, sq)); n += 1
    # feather: soft values appear
    assert any(0.0 < v < 1.0 for r in m.process(sq, feather=2) for v in r); n += 1
    # inside only never goes above the hard mask; outside only never below
    inside = m.process(sq, feather=2, edge="inside only")
    assert all(i <= s + 1e-9 for ri, rs in zip(inside, sq) for i, s in zip(ri, rs)); n += 1
    outside = m.process(sq, feather=2, edge="outside only")
    assert all(o >= s - 1e-9 for ro, rs in zip(outside, sq) for o, s in zip(ro, rs)); n += 1
    # grow then feather: the grown block stays solid in its middle
    both = m.process(sq, grow=2, feather=1, edge="inside only")
    assert both[6][5] > 0.999 and both[6][3] > 0.0; n += 1
    # coverage
    assert near(m.coverage(sq), 100.0 * 16 / 144); n += 1
    assert near(m.coverage([[0.0, 0.0]]), 0.0); n += 1
    # refusals
    assert raises(m.process, sq, threshold=1.5); n += 1
    assert raises(m.process, sq, grow=1000); n += 1
    assert raises(m.process, sq, feather=-1); n += 1
    assert raises(m.process, sq, feather=1, edge="sideways"); n += 1
    assert raises(m.check_settings, 0, 0, 0, "centred", "pink", 0.5); n += 1
    assert raises(m.check_settings, 0, 0, 0, "centred", "red", 2.0); n += 1
    m.check_settings(0.0, 0, 0, "centred", "red", 0.5); n += 1
    # info
    t = m.tools_info(0.0, 0, 0, "centred", False, False, 11.1, 11.1)
    assert "neutral" in t; n += 1
    t = m.tools_info(0.5, 4, 8, "inside only", True, False, 10.0, 25.0, "mask 8x8 was stretched to the picture size 16x16")
    assert "hardened at 0.5" in t and "grown 4 px" in t and "feathered 8 px (inside only)" in t and "inverted" in t and "stretched" in t; n += 1
    assert t.index("hardened") < t.index("grown") < t.index("feathered") < t.rindex("inverted"); n += 1
    t = m.tools_info(0.0, -3, 0, "centred", False, True, 10.0, 90.0)
    assert "shrunk 3 px" in t and t.index("inverted first") < t.index("shrunk"); n += 1
    t = m.tools_info(0.5, 0, 0, "centred", False, False, 0.0, 0.0)
    assert "empty" in t; n += 1
    # torch part: only when torch is installed (the selftest Python has none)
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        node = m.SYMaskTools()
        mk = torch.tensor(block(12, 12, 4, 8, 4, 8)).unsqueeze(0)
        out, prev, info = node.run(mk)
        assert torch.equal(out, mk) and tuple(prev.shape) == (1, 12, 12, 3) and "neutral" in info; n += 1
        # torch matches the pure function
        for kw in ({"threshold": 0.5, "grow": 1}, {"grow": -1}, {"feather": 2}, {"feather": 2, "edge": "inside only"},
                   {"feather": 2, "edge": "outside only"}, {"grow": 2, "feather": 1, "invert": True}, {"invert_first": True, "threshold": 0.5}):
            out, _, _ = node.run(mk, **kw)
            ref = m.process(block(12, 12, 4, 8, 4, 8), **kw)
            assert all(near(float(a), b, 1e-5) for ra, rb in zip(out[0], ref) for a, b in zip(ra, rb)), kw
            n += 1
        img = torch.zeros(1, 12, 12, 3)
        out, prev, info = node.run(mk, image=img, overlay_colour="red", overlay_opacity=1.0)
        assert near(float(prev[0, 5, 5, 0]), 1.0) and near(float(prev[0, 0, 0, 0]), 0.0) and near(float(prev[0, 5, 5, 1]), 0.0); n += 1
        img = torch.zeros(2, 24, 24, 3)
        out, prev, info = node.run(mk, image=img, grow=1)
        assert tuple(out.shape) == (2, 24, 24) and tuple(prev.shape) == (2, 24, 24, 3) and "stretched" in info; n += 1
        out, prev, info = node.run(torch.zeros(1, 8, 8))
        assert float(out.max()) == 0.0 and "neutral" in info; n += 1
        assert raises(node.run, torch.zeros(2, 2, 2, 2)); n += 1
        assert raises(node.run, mk, threshold=2.0); n += 1
        assert raises(node.run, mk, image=torch.zeros(1, 8, 8, 1)); n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
