import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_before_after as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


OK = ("split vertical", 0.5, 2, "white", "resize after to before", 4.0, "all pictures")


def run():
    n = 0
    # settings
    m.check_settings(*OK); n += 1
    for idx, bad in ((0, "spin"), (1, 1.5), (1, -0.1), (2, 21), (2, -1), (3, "pink"), (4, "x"), (5, 0.5), (5, 21.0), (6, "some")):
        args = list(OK)
        args[idx] = bad
        assert raises(m.check_settings, *args), (idx, bad)
        n += 1
    # split maths
    assert m.split_cut(0.5, 100) == 50 and m.split_cut(0, 100) == 0 and m.split_cut(1, 100) == 100 and m.split_cut(0.254, 100) == 25; n += 1
    assert m.split_cut(0.5, 7) in (3, 4); n += 1
    assert m.line_bounds(50, 2, 100) == (49, 51) and m.line_bounds(50, 3, 100) == (49, 52); n += 1
    assert m.line_bounds(0, 4, 100) == (0, 2) and m.line_bounds(100, 4, 100) == (98, 100); n += 1
    assert m.line_bounds(50, 0, 100) == (49 + 1, 50) or m.line_bounds(50, 0, 100)[0] == m.line_bounds(50, 0, 100)[1]; n += 1
    assert m.checker_block(64, 128) == 8 and m.checker_block(4, 4) == 1; n += 1
    # pixel choice
    assert m.pick_before("split vertical", 9, 0, 20, 10, 0.5) and not m.pick_before("split vertical", 10, 0, 20, 10, 0.5); n += 1
    assert m.pick_before("split horizontal", 0, 4, 20, 10, 0.5) and not m.pick_before("split horizontal", 0, 5, 20, 10, 0.5); n += 1
    assert m.pick_before("checkerboard", 0, 0, 64, 64, 0) and not m.pick_before("checkerboard", 8, 0, 64, 64, 0) and m.pick_before("checkerboard", 8, 8, 64, 64, 0); n += 1
    assert raises(m.pick_before, "blend", 0, 0, 8, 8, 0.5); n += 1
    # size choice
    assert m.target_size("resize after to before", (100, 50), (40, 40)) == (100, 50); n += 1
    assert m.target_size("resize both to the smaller", (100, 50), (40, 40)) == (40, 40); n += 1
    assert m.target_size("resize both to the smaller", (30, 30), (40, 40)) == (30, 30); n += 1
    assert m.target_size("refuse on mismatch", (8, 8), (8, 8)) == (8, 8); n += 1
    e = raises(m.target_size, "refuse on mismatch", (8, 8), (9, 8))
    assert e and "8x8" in e and "9x8" in e; n += 1
    assert m.pic_index(5, 2) == 1 and raises(m.pic_index, 0, 0); n += 1
    # label font and plan
    for ch in "before":
        assert ch in m.FONT
    for ch in "after":
        assert ch in m.FONT
    for rows in m.FONT.values():
        assert len(rows) == m.GLYPH_H and all(len(r) == m.GLYPH_W for r in rows)
    n += 1
    bm = m.render_text("before", 1, 1)
    assert len(bm) == 9 and len(bm[0]) == 6 * 6 - 1 + 2 and any(any(r) for r in bm) and not any(bm[0]) and not any(bm[-1]); n += 1
    bm3 = m.render_text("after", 3, 1)
    assert len(bm3) == 27 and len(bm3[0]) == (5 * 6 - 1 + 2) * 3; n += 1
    assert raises(m.render_text, "Zed"); n += 1
    assert m.label_scale(64, 64) == 1 and m.label_scale(1024, 2048) == 6; n += 1
    plan = m.label_plan("split vertical", 100, 200, 0.25, 2)
    assert plan[0][:5] == ("before", 0, 0, 50, 100) and plan[1][:5] == ("after", 50, 0, 200, 100) and plan[1][5] == "right"; n += 1
    plan = m.label_plan("side by side", 100, 200, 0.5, 4)
    assert plan[1][1] == 204 and plan[1][3] == 404; n += 1
    plan = m.label_plan("top and bottom", 100, 200, 0.5, 4)
    assert plan[1][2] == 104 and plan[1][4] == 204; n += 1
    assert m.label_plan("difference", 100, 200, 0.5, 2) == [] and m.label_plan("blend", 8, 8, 0.5, 1) == []; n += 1
    assert m.place_label((0, 0, 100, 50), 40, 10, 4, "left") == (4, 4); n += 1
    assert m.place_label((0, 0, 100, 50), 40, 10, 4, "right") == (56, 4); n += 1
    assert m.place_label((0, 0, 30, 50), 40, 10, 4, "left") is None and m.place_label((0, 0, 100, 12), 40, 10, 4, "left") is None; n += 1
    # info
    t = m.info_text("split vertical", (8, 8), (4, 4), (8, 8), True, 2, 1, 2, 12.345, "labels drawn", 0.5)
    for need in ("Before 8x8, after 4x4", "resized to 8x8", "at 50%", "2 comparison pictures", "before has 2 and after has 1", "12.35%", "labels drawn"):
        assert need in t, need
        n += 1
    # torch part
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        node = m.SYBeforeAfter()
        assert node.RETURN_NAMES == ("comparison", "info") and m.NODE_DISPLAY_NAME_MAPPINGS["SYBeforeAfter"] == "Before After SY"; n += 1
        bef = torch.zeros(1, 20, 40, 3)
        aft = torch.ones(1, 20, 40, 3)
        # split vertical, no line, no labels
        out, info = node.run(bef, aft, "split vertical", 0.25, 0, "white", False)
        assert out.shape == (1, 20, 40, 3) and float(out[0, 5, 9, 0]) == 0.0 and float(out[0, 5, 10, 0]) == 1.0; n += 1
        # every pixel agrees with the pure rule
        ok = all((float(out[0, y, x, 0]) == 0.0) == m.pick_before("split vertical", x, y, 40, 20, 0.25) for y in range(20) for x in range(40))
        assert ok; n += 1
        out, _ = node.run(bef, aft, "split horizontal", 0.5, 0, "white", False)
        ok = all((float(out[0, y, x, 0]) == 0.0) == m.pick_before("split horizontal", x, y, 40, 20, 0.5) for y in range(20) for x in range(40))
        assert ok; n += 1
        out, _ = node.run(bef, aft, "checkerboard", 0.5, 2, "red", False)
        ok = all((float(out[0, y, x, 0]) == 0.0) == m.pick_before("checkerboard", x, y, 40, 20, 0.5) for y in range(20) for x in range(40))
        assert ok and out.shape == bef.shape; n += 1
        # line colour and width
        out, _ = node.run(bef, aft, "split vertical", 0.5, 4, "red", False)
        assert torch.equal(out[0, 3, 18:22], torch.tensor([1.0, 0.0, 0.0]).expand(4, 3)); n += 1
        assert float(out[0, 3, 17, 0]) == 0.0 and float(out[0, 3, 22, 0]) == 1.0; n += 1
        out, _ = node.run(bef, aft, "split horizontal", 0.5, 2, "yellow", False)
        assert torch.equal(out[0, 9:11, 5], torch.tensor([1.0, 1.0, 0.0]).expand(2, 3)); n += 1
        # position 0 and 1 show only one picture
        out, _ = node.run(bef, aft, "split vertical", 0.0, 0, "white", False)
        assert torch.equal(out, aft); n += 1
        out, _ = node.run(bef, aft, "split vertical", 1.0, 0, "white", False)
        assert torch.equal(out, bef); n += 1
        # side by side and top and bottom
        out, _ = node.run(bef, aft, "side by side", 0.5, 3, "blue", False)
        assert out.shape == (1, 20, 83, 3) and float(out[0, 0, 39, 0]) == 0.0 and float(out[0, 0, 40, 2]) == 1.0 and float(out[0, 0, 40, 0]) == 0.0 and float(out[0, 0, 43, 0]) == 1.0; n += 1
        out, _ = node.run(bef, aft, "top and bottom", 0.5, 0, "blue", False)
        assert out.shape == (1, 40, 40, 3) and float(out[0, 19, 0, 0]) == 0.0 and float(out[0, 20, 0, 0]) == 1.0; n += 1
        # difference with gain
        a1 = torch.full((1, 8, 8, 3), 0.5)
        a2 = torch.full((1, 8, 8, 3), 0.55)
        out, info = node.run(a1, a2, "difference", difference_gain=4.0)
        assert abs(float(out[0, 0, 0, 0]) - 0.2) < 1e-4 and "5.00%" in info; n += 1
        out, _ = node.run(a1, a2, "difference", difference_gain=20.0)
        assert float(out[0, 0, 0, 0]) == 1.0; n += 1
        out, info = node.run(a1, a1, "difference")
        assert float(out.max()) == 0.0 and "0.00%" in info; n += 1
        # blend
        out, _ = node.run(bef, aft, "blend", 0.25)
        assert abs(float(out[0, 3, 3, 0]) - 0.25) < 1e-6; n += 1
        # size handling
        small = torch.ones(1, 10, 10, 3)
        out, info = node.run(bef, small, "side by side", line_width=0, labels=False)
        assert out.shape == (1, 20, 80, 3) and "resized to 40x20" in info; n += 1
        out, info = node.run(bef, small, "side by side", line_width=0, labels=False, match_size="resize both to the smaller")
        assert out.shape == (1, 10, 20, 3) and "resized to 10x10" in info; n += 1
        e = raises(node.run, bef, small, match_size="refuse on mismatch")
        assert e and "differ in size" in e; n += 1
        # batches
        b3 = torch.rand(3, 8, 8, 3)
        a2b = torch.rand(2, 8, 8, 3)
        out, info = node.run(b3, a2b, "blend", 1.0, batch_mode="all pictures")
        assert out.shape[0] == 3 and torch.allclose(out[2], a2b[0], atol=1e-6) and "before has 3 and after has 2" in info; n += 1
        out, info = node.run(b3, a2b, "blend", 1.0, batch_mode="first picture only")
        assert out.shape[0] == 1 and torch.allclose(out[0], a2b[0], atol=1e-6) and "1 comparison picture;" in info; n += 1
        # alpha dropped, grey repeated, bad shapes refused
        out, _ = node.run(torch.rand(1, 8, 8, 4), torch.rand(1, 8, 8, 1), "blend")
        assert out.shape == (1, 8, 8, 3); n += 1
        assert raises(node.run, torch.rand(8, 8, 3), aft); n += 1
        assert raises(node.run, torch.rand(0, 8, 8, 3), aft); n += 1
        assert raises(node.run, bef, aft, mode="nope"); n += 1
        # labels: drawn on a big enough picture, change pixels near the corner, and sit in the right region
        big_b = torch.full((1, 160, 320, 3), 0.5)
        big_a = torch.full((1, 160, 320, 3), 0.5)
        plain, _ = node.run(big_b, big_a, "split vertical", 0.5, 0, "white", False)
        lab, info = node.run(big_b, big_a, "split vertical", 0.5, 0, "white", True)
        assert "labels drawn" in info and not torch.equal(plain, lab); n += 1
        diff = (plain != lab).any(dim=-1)[0]
        ys, xs = diff.nonzero(as_tuple=True)
        assert int(ys.max()) < 40 and (int(xs.min()) < 60 or int(xs.max()) > 260); n += 1
        assert float(lab.min()) >= 0.0 and float(lab.max()) <= 1.0; n += 1
        # labels that do not fit are left out, and other modes say why
        tiny, info = node.run(torch.zeros(1, 12, 12, 3), torch.ones(1, 12, 12, 3), "split vertical", 0.5, 2, "white", True)
        assert "of 2 fit" in info or "labels drawn" in info; n += 1
        _, info = node.run(bef, aft, "blend", labels=True)
        assert "only drawn for" in info; n += 1
        # input pictures are not changed
        keep = bef.clone()
        node.run(bef, aft, "split vertical", 0.5, 4, "red", True)
        assert torch.equal(bef, keep); n += 1
        # output stays 0..1
        out, _ = node.run(torch.rand(2, 33, 47, 3), torch.rand(2, 33, 47, 3), "difference", difference_gain=20.0)
        assert float(out.min()) >= 0.0 and float(out.max()) <= 1.0; n += 1
        # slider pair: first picture only, both at one size, refusal passes through
        sb, sa = m.slider_pair(torch.rand(3, 10, 20, 3), torch.rand(2, 5, 8, 4), "resize after to before")
        assert tuple(sb.shape) == (1, 10, 20, 3) and tuple(sa.shape) == (1, 10, 20, 3); n += 1
        assert raises(m.slider_pair, torch.zeros(1, 4, 4, 3), torch.zeros(1, 8, 8, 3), "refuse on mismatch"); n += 1
        # the node also hands the browser two temp files (before first, so before is on the left)
        import tempfile
        import types
        tmp = tempfile.mkdtemp()
        fake = types.ModuleType("folder_paths")
        fake.get_temp_directory = lambda: tmp
        old_fp = sys.modules.get("folder_paths")
        sys.modules["folder_paths"] = fake
        try:
            res = node.run(torch.zeros(1, 6, 6, 3), torch.ones(1, 6, 6, 3))
        finally:
            if old_fp is None:
                del sys.modules["folder_paths"]
            else:
                sys.modules["folder_paths"] = old_fp
        assert isinstance(res, dict) and len(res["ui"]["sy_compare"]) == 2 and len(res["result"]) == 2; n += 1
        files = res["ui"]["sy_compare"]
        assert files[0]["filename"].endswith("_a.png") and files[1]["filename"].endswith("_b.png"); n += 1
        from PIL import Image
        assert Image.open(os.path.join(tmp, files[0]["filename"])).getpixel((0, 0))[0] == 0; n += 1
        assert Image.open(os.path.join(tmp, files[1]["filename"])).getpixel((0, 0))[0] == 255; n += 1
        assert getattr(m.SYBeforeAfter, "OUTPUT_NODE", False) is True; n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
