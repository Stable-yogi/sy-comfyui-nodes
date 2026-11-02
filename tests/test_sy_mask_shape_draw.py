import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_shape_draw as m


def run():
    n = 0
    sv = m.shape_value
    # rectangle: inside 1, outside 0
    assert sv("rectangle", 0.5, 0.5, {"width": 100, "height": 100}) == 1.0
    assert sv("rectangle", 0.05, 0.5, {"width": 100, "height": 100}) == 0.0
    assert sv("rectangle", 0.74, 0.5, {"width": 100, "height": 100}) == 1.0
    assert sv("rectangle", 0.76, 0.5, {"width": 100, "height": 100}) == 0.0
    n += 4
    # ellipse: corner of its box is outside, middle of an edge is inside
    assert sv("ellipse", 0.5, 0.5, {"width": 100, "height": 100}) == 1.0
    assert sv("ellipse", 0.74, 0.74, {"width": 100, "height": 100}) == 0.0
    assert sv("ellipse", 0.7, 0.5, {"width": 100, "height": 100}) == 1.0
    n += 3
    # rounded rectangle cuts the corner that the plain rectangle keeps
    corner = {"width": 100, "height": 100, "sx": 0.5, "sy": 0.5}
    assert sv("rectangle", 0.745, 0.745, corner) == 1.0
    assert sv("rounded rectangle", 0.745, 0.745, corner) == 0.0
    assert sv("rounded rectangle", 0.5, 0.5, corner) == 1.0
    n += 3
    # feather: edge is half, then falls off smoothly
    fe = {"width": 100, "height": 100, "feather": 0.1}
    mid = sv("rectangle", 0.75, 0.5, fe)
    assert 0.4 < mid < 0.6
    assert sv("rectangle", 0.7, 0.5, fe) > mid > sv("rectangle", 0.8, 0.5, fe)
    n += 2
    # linear gradient: 0 on the left, 0.5 in the middle, 1 on the right; angle 180 flips it
    lin = {"width": 100, "height": 100, "sx": 1.0}
    assert sv("linear gradient", 0.0, 0.5, lin) == 0.0
    assert abs(sv("linear gradient", 0.5, 0.5, lin) - 0.5) < 1e-9
    assert sv("linear gradient", 1.0, 0.5, lin) == 1.0
    flip = dict(lin, angle=180.0)
    assert abs(sv("linear gradient", 0.0, 0.5, flip) - 1.0) < 1e-9
    n += 4
    # radial gradient: 1 in the middle, 0 at the rim
    rad = {"width": 100, "height": 100, "sx": 1.0, "sy": 1.0}
    assert sv("radial gradient", 0.5, 0.5, rad) == 1.0
    assert sv("radial gradient", 1.0, 0.5, rad) == 0.0
    assert 0.4 < sv("radial gradient", 0.75, 0.5, rad) < 0.6
    n += 3
    # rotation of a wide bar by 90 degrees makes it tall
    bar = {"width": 100, "height": 100, "sx": 0.8, "sy": 0.1, "angle": 90.0}
    assert sv("rectangle", 0.5, 0.15, bar) == 1.0
    assert sv("rectangle", 0.15, 0.5, bar) == 0.0
    n += 2
    # refusal text
    for call in (lambda: m.check_args(4, 100, "ellipse"), lambda: m.check_args(100, 9000, "ellipse"),
                 lambda: m.check_args(100, 100, "star"), lambda: sv("star", 0.5, 0.5, {})):
        try:
            call()
            raise SystemExit("bad args must raise")
        except ValueError as e:
            assert "must" in str(e)
        n += 1
    assert len(m.SHAPES) == 5
    assert m.SYMaskShapeDraw.RETURN_TYPES == ("MASK",)
    n += 2
    return n
