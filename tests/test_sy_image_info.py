import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_info as m


class FakeImg:
    def __init__(self, shape):
        self.shape = shape


def run():
    assert m.image_dims((1, 512, 768, 3)) == (768, 512, 1, 512 * 768 / 1e6)
    assert m.image_dims((4, 1000, 1000, 3))[2:] == (4, 1.0)
    assert m.image_dims((64, 32, 3))[:3] == (32, 64, 1)
    assert m.image_dims([2, 10, 20, 4])[:3] == (20, 10, 2)
    try:
        m.image_dims((1,))
        raise SystemExit("bad shape must raise")
    except ValueError:
        pass
    img = FakeImg((2, 100, 200, 3))
    out = m.SYImageInfo().run(img)
    assert out[0] is img and out[1:4] == (200, 100, 2)
    assert abs(out[4] - 0.02) < 1e-9
    assert m.SYImageInfo.RETURN_NAMES == ("image", "width", "height", "batch", "megapixels", "channels", "aspect", "info")
    assert out[5] == 3 and out[6] == "2:1 (2.000)" and "200x100" in out[7]
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYImageInfo"] == "Image Info SY"
    n = 9
    assert m.aspect_text(1024, 768) == "4:3 (1.333)"; n += 1
    assert m.aspect_text(1920, 1080) == "16:9 (1.778)"; n += 1
    assert m.aspect_text(512, 512) == "1:1 (1.000)"; n += 1
    assert m.aspect_text(1000, 667).startswith("about 3:2"); n += 1
    assert m.aspect_text(1013, 599) == "1.691"; n += 1
    try:
        m.aspect_text(0, 5)
        raise SystemExit("zero size must raise")
    except ValueError:
        n += 1
    assert m.size_notes(1024, 1024, 1, 1.05) == []; n += 1
    assert "multiple of 8" in m.size_notes(1023, 1024, 1, 1.0)[0]; n += 1
    assert "multiple of 64" in m.size_notes(1032, 1024, 1, 1.0)[0]; n += 1
    assert any("large" in x for x in m.size_notes(4096, 4096, 1, 16.7)); n += 1
    assert any("4n+1" in x for x in m.size_notes(512, 512, 9, 0.26)) and not any("4n+1" in x for x in m.size_notes(512, 512, 8, 0.26)); n += 1
    t = m.info_text(768, 512, 1, 0.39, 4)
    assert t.startswith("768x512, shape 3:2 (1.500), 0.39 megapixels, 1 picture(s), RGB with transparency") and t.endswith("."); n += 1
    try:
        m.SYImageInfo().run(FakeImg((1, 0, 5, 3)))
        raise SystemExit("empty picture must raise")
    except ValueError as e:
        assert "no pixels" in str(e); n += 1
    return n
