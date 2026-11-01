import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_tiled_upscale as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    # grid covers the whole picture exactly, for many sizes
    for (w, h, t, o) in ((1000, 700, 512, 32), (512, 512, 512, 32), (300, 200, 512, 32), (992, 992, 512, 32), (1500, 129, 256, 64), (7, 9, 128, 0)):
        cover = [[0] * w for _ in range(h)]
        for (x, y, tw, th, lx, tx, ly, ty) in m.tile_grid(w, h, t, o):
            assert 0 <= x and x + tw <= w and 0 <= y and y + th <= h
            for yy in range(y, y + th):
                for xx in range(x, x + tw):
                    cover[yy][xx] += 1
        assert all(v >= 1 for row in cover for v in row), (w, h, t, o)
        n += 1
    assert raises(m.tile_grid, 100, 100, 64, 64) and raises(m.tile_grid, 100, 100, 64, -1); n += 1
    # 1D weights: ramps of neighbour tiles sum to 1 in a regular overlap (992 = 512 + 480, overlap 32)
    plan = m.axis_plan(992, 512, 32)
    assert [p[0] for p in plan] == [0, 480] and plan[0][3] == 32 and plan[1][2] == 32; n += 1
    tot = [0.0] * 992
    for (s, ln, lead, trail) in plan:
        for i, wt in enumerate(m.feather_1d(ln, lead, trail)):
            tot[s + i] += wt
    assert all(abs(v - 1.0) < 1e-9 for v in tot); n += 1
    # three tiles
    plan = m.axis_plan(1440, 512, 32)
    tot = [0.0] * 1440
    for (s, ln, lead, trail) in plan:
        for i, wt in enumerate(m.feather_1d(ln, lead, trail)):
            tot[s + i] += wt
    assert len(plan) == 3 and all(abs(v - 1.0) < 1e-9 for v in tot[:1000]); n += 1
    assert m.axis_plan(100, 512, 32) == [(0, 100, 0, 0)]; n += 1
    # retry sizes
    assert m.halve_tile(512) == 256 and m.halve_tile(256) == 128 and m.halve_tile(128) is None and m.halve_tile(200) == 128; n += 1
    assert "halved 2 times" in m.size_info((10, 10), (20, 20), 2, 4, 128, 2, 1) and "1 tile " in m.size_info((1, 1), (2, 2), 2, 1, 128, 0, 1); n += 1
    try:
        import torch
        import torch.nn.functional as F
    except ImportError:
        return n

    def fake(x):
        return F.interpolate(x.movedim(-1, 1), scale_factor=2, mode="nearest").movedim(1, -1)

    torch.manual_seed(1)
    img = torch.rand(2, 70, 90, 3)
    ref = fake(img)
    for blend in ("feather", "none"):
        out, s, count = m.upscale_tiled(img, fake, 2, 32, 8, blend)
        assert s == 2 and tuple(out.shape) == (2, 140, 180, 3) and count > 1
        assert float((out - ref).abs().max()) < 1e-5, blend   # nearest model is position-independent, so tiles join perfectly
        n += 1
    out, s, count = m.upscale_tiled(img, fake, 0, 40, 8)       # scale found by itself
    assert s == 2 and float((out - ref).abs().max()) < 1e-5; n += 1
    # a model whose tiles differ per call still gives weights that normalise: constant tiles stay constant
    out, s, count = m.upscale_tiled(torch.ones(1, 50, 50, 3) * 0.5, lambda t: fake(t) * 1.0, 2, 24, 8)
    assert float((out - 0.5).abs().max()) < 1e-6; n += 1
    assert raises(m.upscale_tiled, torch.rand(3, 3), fake, 2, 32, 8) and raises(m.upscale_tiled, img, fake, 2, 32, 8, "x"); n += 1
    assert raises(m.upscale_tiled, img, lambda t: t, 2, 32, 8); n += 1   # model did not enlarge
    return n
