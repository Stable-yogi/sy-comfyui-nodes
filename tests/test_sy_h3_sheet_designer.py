import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_sheet_designer as m


def _raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    # presets
    std = m.pick_views("Standard 5 (2 faces + 3 bodies)")
    assert std == ("face_front", "face_left", "body_front", "body_side", "body_back"); n += 1
    assert len(m.pick_views("All 13")) == 13; n += 1
    assert m.pick_views("Custom (use the views box)", "body_back, face_front") == ("face_front", "body_back"); n += 1
    assert _raises(m.pick_views, "Custom (use the views box)", ""); n += 1
    assert _raises(m.pick_views, "nope"); n += 1
    assert _raises(m.parse_views, "face_front, elbow"); n += 1
    assert m.parse_views("feet;hands\nfeet") == ("hands", "feet"); n += 1
    # layout: every view once, panels inside the sheet, no overlap
    for name in m.PRESETS:
        if not m.PRESETS[name]:
            continue
        views = m.pick_views(name)
        panels, (sw, sh) = m.plan_layout(views)
        assert sorted(p[0] for p in panels) == sorted(views), name
        for v, x, y, w, h in panels:
            assert x >= 0 and y >= 0 and x + w <= sw + 1e-6 and y + h <= sh + 1e-6, (name, v)
        for i, a in enumerate(panels):
            for b in panels[i + 1:]:
                sep = a[1] + a[3] <= b[1] + 1e-6 or b[1] + b[3] <= a[1] + 1e-6 or a[2] + a[4] <= b[2] + 1e-6 or b[2] + b[4] <= a[2] + 1e-6
                assert sep, (name, a[0], b[0])
        n += 1
    # sizes: multiples of 32, near the megapixels
    _, (sw, sh) = m.plan_layout(std)
    for size, mp in m.SIZES.items():
        w, h = m.sheet_size(sw / sh, size)
        assert w % 32 == 0 and h % 32 == 0; n += 1
        assert abs(w * h / 1048576.0 - mp) / mp < 0.05, (size, w, h); n += 1
        assert w > h; n += 1
    assert _raises(m.sheet_size, 1.0, "3 MP"); n += 1
    # prompt
    p = m.build_prompt(std)
    assert "<Picture 1>" in p and "<Picture 2>" in p; n += 1
    assert "No text, no letters, no numbers, no labels" in p; n += 1
    assert "exactly once" in p and "profile looking to the left" in p; n += 1
    assert "face_front" not in p and "[" not in p; n += 1  # no key names or brackets that could print as text
    assert "<Picture 2>" not in m.build_prompt(std, use_guide=False); n += 1
    assert "anime" in m.build_prompt(std, "anime"); n += 1
    assert "Character notes: red scarf" in m.build_prompt(std, notes="  red\n scarf "); n += 1
    assert "one single view" in m.build_prompt(("body_front",)); n += 1
    assert "rows of three" in m.build_prompt(m.pick_views("Head 6 (6 head views)")); n += 1
    assert _raises(m.build_prompt, std, "oil"); n += 1
    assert "5 views" in m.describe(std, 2720, 1536); n += 1
    # node shape
    it = m.SYH3SheetDesigner.INPUT_TYPES()
    assert set(it["required"]) == {"preset", "size", "style", "use_layout_guide"}; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYH3SheetDesigner"] == "H3 Sheet Designer SY"; n += 1
    # guide picture (needs numpy + PIL; skip quietly if missing)
    try:
        import numpy  # noqa: F401
        from PIL import Image  # noqa: F401
    except ImportError:
        return n
    g = m.draw_guide(std, 640, 360)
    assert g.shape == (360, 640, 3) and g.max() <= 1.0; n += 1
    assert g.min() < 0.95 and g[0, 0].tolist() == [1.0, 1.0, 1.0]; n += 1
    return n
