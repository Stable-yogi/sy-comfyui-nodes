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
    assert m.SYImageInfo.RETURN_NAMES == ("image", "width", "height", "batch", "megapixels")
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYImageInfo"] == "Image Info SY"
    return 9
