import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_image_size as m

S4, S16 = list(m.SIZES)[0], list(m.SIZES)[2]


def refuses(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return ""


def run():
    n = 0
    assert m.h3_size(S4, "1:1 square") == (2048, 2048); n += 1          # the tested 4 MP size
    assert m.h3_size(S16, "1:1 square") == (4096, 4096); n += 1         # the tested 16 MP size
    for size in m.SIZES:
        for shape, (a, b) in m.SHAPES.items():
            w, h = m.h3_size(size, shape)
            assert w % 32 == 0 and h % 32 == 0, (size, shape, w, h)
            assert abs(w * h / (m.SIZES[size] * 1048576) - 1) < 0.06, (size, shape, w, h)
            assert abs((w / h) - (a / b)) < 0.03, (size, shape, w, h)
    n += 1
    w, h = m.h3_size(S4, "9:16 tall")
    assert h > w; n += 1
    assert "unknown size" in refuses(m.h3_size, "2 MP", "1:1 square"); n += 1
    assert "unknown shape" in refuses(m.h3_size, S4, "7:1"); n += 1
    assert m.version_tuple("0.45.1") == (0, 45, 1) and m.version_tuple("v0.45.0-12") == (0, 45, 0); n += 1
    assert m.version_tuple("0.45") == (0, 45, 0) and m.version_tuple("") is None and m.version_tuple("abc") is None; n += 1
    assert "fine" in m.version_note("0.45.0") and "too old" in m.version_note("0.43.0") and "unknown" in m.version_note(""); n += 1
    it = m.SYH3ImageSize.INPUT_TYPES()["required"]
    assert it["size"][1]["default"] == S4 and it["shape"][1]["default"] == "1:1 square"; n += 1
    w, h, info = m.SYH3ImageSize().run(S4, "1:1 square")
    assert (w, h) == (2048, 2048) and "H3 IMAGE SIZE" in info; n += 1
    assert "SYH3ImageSize" in m.NODE_CLASS_MAPPINGS and m.NODE_DISPLAY_NAME_MAPPINGS["SYH3ImageSize"].endswith(" SY"); n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
