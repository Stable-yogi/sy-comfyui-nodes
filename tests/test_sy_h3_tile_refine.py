import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_tile_refine as m
import _sy_h3_windows as win


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.to_cells(896) == 56 and m.to_cells(704) == 44 and m.to_cells(20) == 2 and m.to_cells(1000) == 62; n += 1
    # the tiles cover the whole latent and stay inside it
    for (cw, ch, tw, th, ox, oy) in ((120, 68, 896, 704, 256, 320), (60, 34, 896, 704, 256, 320), (120, 68, 2048, 2048, 256, 256), (120, 68, 512, 512, 0, 0), (84, 48, 640, 384, 128, 96)):
        cover = [[0] * cw for _ in range(ch)]
        for (x, y, w, h, lx, tx, ly, ty) in m.tile_plan(cw, ch, tw, th, ox, oy):
            assert 0 <= x and x + w <= cw and 0 <= y and y + h <= ch
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    cover[yy][xx] += 1
        assert all(v >= 1 for row in cover for v in row), (cw, ch, tw, th)
        n += 1
    # 1920 x 1088 with the default tile: every tile is 896 x 704
    plan = m.tile_plan(120, 68, 896, 704, 256, 320)
    assert len(plan) == 6 and all(p[2] == 56 and p[3] == 44 for p in plan), plan; n += 1
    # a tile bigger than the video = one tile, no blending
    plan = m.tile_plan(60, 34, 2048, 2048, 256, 256)
    assert plan == [(0, 0, 60, 34, 0, 0, 0, 0)], plan; n += 1
    assert raises(m.tile_plan, 120, 68, 256, 256, 256, 0) and raises(m.tile_plan, 120, 68, 256, 256, 0, 512); n += 1
    assert m.plan_info(120, 68, m.tile_plan(120, 68, 896, 704, 256, 320), 23) == "1920 x 1088 pixels, 23 latent frames, 6 tiles of 896 x 704 pixels"; n += 1
    assert m.plan_info(60, 34, m.tile_plan(60, 34, 2048, 2048, 0, 0), 5).endswith("1 tile of 960 x 544 pixels"); n += 1
    assert m.plan_info(120, 68, m.tile_plan(120, 68, 896, 704, 256, 320), 57, 3).endswith("6 tiles of 896 x 704 pixels, 3 time windows"); n += 1
    # time windows: valid lengths, block-edge starts, full cover, the last one ends on the last frame
    assert win.frames_for_tokens(7) == 22 and win.frames_for_tokens(57) == 192 and win.tokens_for_frames(124) == 37 and win.tokens_for_frames(5) == 2; n += 1
    assert win.plan_windows(57, 0, 22) == [(0, 57)] and win.plan_windows(57, 192, 22) == [(0, 57)] and win.plan_windows(57, 5000, 22) == [(0, 57)]; n += 1
    for (t, wf, ov) in ((57, 124, 22), (117, 124, 22), (292, 124, 39), (117, 56, 5), (62, 39, 39), (117, 22, 22), (42, 124, 22), (47, 124, 22)):
        plan = win.plan_windows(t, wf, ov)
        got = set()
        for (t0, tn) in plan:
            assert t0 % 5 == 0 and tn % 5 == 2 and t0 + tn <= t, (t, wf, ov, plan)
            got.update(range(t0, t0 + tn))
        assert got == set(range(t)) and plan[-1][0] + plan[-1][1] == t, (t, wf, ov, plan)
        assert all(a[0] < b[0] < a[0] + a[1] for a, b in zip(plan, plan[1:])), (t, wf, ov, plan)
        n += 1
    # the sound pieces follow the windows and the last one reaches the end
    plan = win.plan_windows(117, 124, 22)
    spans = [win.audio_span(plan, i, 695) for i in range(len(plan))]
    assert spans[0][0] == 0 and spans[-1][1] == 695 and all(0 <= a < b <= 695 for a, b in spans), spans; n += 1
    fade = win.ease_in_out(7)
    assert len(fade) == 7 and 0 < fade[0] < 0.1 and 0.9 < fade[-1] < 1 and fade == sorted(fade) and abs(fade[3] - 0.5) < 1e-9; n += 1
    # a one-frame guide moves to window time, or leaves the windows that do not hold it
    kf = [{"resolved_frame_index": 0}, {"resolved_frame_index": 200}]
    assert win.window_keyframes(kf, 0, 37) == [{"resolved_frame_index": 0}]; n += 1
    assert win.window_keyframes(kf, 50, 87) == [{"resolved_frame_index": 30}]; n += 1
    keys = m.SYH3TileRefine.INPUT_TYPES()
    assert set(keys["required"]) == {"model", "positive", "latent", "sampler", "sigmas"}; n += 1
    assert keys["optional"]["tile_width"][1]["default"] == 896 and keys["optional"]["tile_height"][1]["default"] == 704; n += 1
    assert keys["optional"]["window_frames"][1]["default"] == 0 and keys["optional"]["window_overlap"][1]["default"] == 22 and keys["optional"]["carry"][1]["default"] is True; n += 1
    assert "SYH3TileRefine" in m.NODE_CLASS_MAPPINGS and m.NODE_DISPLAY_NAME_MAPPINGS["SYH3TileRefine"] == "H3 Tile Refine SY"; n += 1
    return n
