import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_big_render_shrink as m


def refuses(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return ""


def run():
    n = 0
    assert m.shrink_size(4096, 4096, "2 MP") == (1440, 1440, True); n += 1      # 16 MP square to 2 MP
    assert m.shrink_size(4096, 4096, "1 MP") == (1024, 1024, True); n += 1
    assert m.shrink_size(2896, 2896, "4 MP")[2] is True; n += 1                  # 8 MP to 4 MP
    w, h, s = m.shrink_size(3840, 2160, "2 MP")
    assert s and w % 16 == 0 and h % 16 == 0 and abs(w / h - 16 / 9) < 0.02 and w * h <= 2 * m.MP; n += 1
    assert m.shrink_size(1024, 1024, "2 MP") == (1024, 1024, False); n += 1      # never enlarges
    assert m.shrink_size(4096, 2048, "long side", 1920) == (1920, 960, True); n += 1
    assert m.shrink_size(1000, 500, "long side", 1920) == (1000, 500, False); n += 1
    assert m.shrink_size(5000, 3000, "1 MP", 0, 1)[0] == int(5000 * (m.MP / 15e6) ** 0.5); n += 1
    assert "unknown target" in refuses(m.shrink_size, 10, 10, "3 MP"); n += 1
    assert "at least 64" in refuses(m.shrink_size, 4096, 4096, "long side", 10); n += 1
    assert "multiple_of" in refuses(m.shrink_size, 4096, 4096, "2 MP", 0, 0); n += 1
    assert m.shrink_plan("clean", 0.3) == ("bicubic", 0.0, 0.0); n += 1
    assert m.shrink_plan("crisp", 0.3) == ("bicubic", 0.3, 1.0); n += 1
    assert m.shrink_plan("soft", 0.9)[0] == "area"; n += 1
    assert "unknown look" in refuses(m.shrink_plan, "sharp", 0.3); n += 1
    assert "between 0 and 1" in refuses(m.shrink_plan, "crisp", 2); n += 1
    info = m.shrink_info(4096, 4096, 1440, 1440, True, "crisp", 0.3)
    assert "16.0 MP" in info and "1440x1440" in info and "sharpen 0.30" in info and "Tip" not in info; n += 1
    assert "Tip" in m.shrink_info(2048, 2048, 1440, 1440, True, "clean", 0); n += 1
    assert m.shrink_info(800, 600, 800, 600, False, "clean", 0).startswith("Left at 800x600"); n += 1
    it = m.SYBigRenderShrink.INPUT_TYPES()
    assert it["required"]["target"][1]["default"] == "2 MP" and "sharpen" in it["optional"]; n += 1
    assert "SYBigRenderShrink" in m.NODE_CLASS_MAPPINGS and m.NODE_DISPLAY_NAME_MAPPINGS["SYBigRenderShrink"] == "Big Render Shrink SY"; n += 1
    try:
        import torch
    except ImportError:
        return n
    img = torch.rand(1, 2048, 1536, 3)
    out, w, h, info = m.SYBigRenderShrink().run(img, "1 MP", "crisp")
    assert tuple(out.shape) == (1, h, w, 3) and float(out.min()) >= 0 and float(out.max()) <= 1; n += 1
    out, w, h, info = m.SYBigRenderShrink().run(torch.rand(2, 512, 512, 4), "2 MP", "clean")
    assert (w, h) == (512, 512) and info.startswith("Left at"); n += 1
    return n
