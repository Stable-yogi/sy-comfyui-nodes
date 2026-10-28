import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_crop_paste as m
import _sy_mask_math as mm


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def solid(h, w, v, c=3):
    return [[[v] * c for _ in range(w)] for _ in range(h)]


def block(w, h, x0, y0, x1, y1):
    return [[1.0 if x0 <= x <= x1 and y0 <= y <= y1 else 0.0 for x in range(w)] for y in range(h)]


def same(a, b):
    return all(abs(u - v) < 1e-9 for ra, rb in zip(a, b) for pa, pb in zip(ra, rb) for u, v in zip(pa, pb))


def run():
    n = 0
    # ---- box maths
    assert mm.clamp_box(2, 2, 10, 10, 6, 6) == (2, 2, 4, 4)
    assert mm.clamp_box(-3, -3, 5, 5, 6, 6) == (0, 0, 2, 2)
    assert mm.clamp_box(20, 20, 5, 5, 6, 6)[2:] == (0, 0)  # fully outside
    n += 3
    assert mm.pad_box((4, 4, 2, 2), 3, 20, 20) == (1, 1, 8, 8)
    assert mm.pad_box((0, 0, 2, 2), 5, 8, 8) == (0, 0, 7, 7)
    n += 2
    assert mm.fit_multiple((10, 10, 13, 9), 8, 100, 100) == (9, 7, 16, 16)
    bx = mm.fit_multiple((10, 10, 13, 9), 8, 100, 100)
    assert bx[2] % 8 == 0 and bx[3] % 8 == 0 and bx[0] <= 10 and bx[0] + bx[2] >= 23
    edge = mm.fit_multiple((95, 95, 5, 5), 8, 100, 100)
    assert edge[0] + edge[2] <= 100 and edge[2] == 8 and edge[0] == 92
    tight = mm.fit_multiple((0, 0, 70, 70), 64, 100, 100)  # 128 will not fit, 64 is too small: use the image
    assert tight == (0, 0, 100, 100)
    assert mm.fit_multiple((3, 3, 5, 5), 1, 50, 50) == (3, 3, 5, 5)
    assert raises(mm.fit_multiple, (0, 0, 4, 4), 0, 10, 10) and raises(mm.fit_multiple, (0, 0, 0, 4), 8, 10, 10)
    n += 7
    # ---- crop info
    info = mm.make_crop_info((4, 6, 8, 8), 32, 32)
    d = mm.parse_crop_info(info)
    assert d == {"x": 4, "y": 6, "w": 8, "h": 8, "image_w": 32, "image_h": 32}
    assert raises(mm.make_crop_info, (30, 0, 8, 8), 32, 32)  # box beyond the image
    assert raises(mm.parse_crop_info, "not json") and raises(mm.parse_crop_info, "[1]")
    bad = json.loads(info)
    bad["w"] = 99
    assert raises(mm.parse_crop_info, json.dumps(bad))
    bad = json.loads(info)
    bad["x"] = "4"
    assert raises(mm.parse_crop_info, json.dumps(bad))
    assert raises(mm.parse_crop_info, None)
    n += 7
    # ---- plan_crop and crop_by_mask
    assert m.plan_crop((8, 8, 4, 4), 4, 8, "error", 64, 64) == (2, 2, 16, 16)
    assert m.plan_crop(None, 0, 8, "whole_image", 30, 20) == (0, 0, 30, 20)
    assert raises(m.plan_crop, None, 0, 8, "error", 30, 20)
    assert raises(m.plan_crop, (0, 0, 2, 2), -1, 8, "error", 30, 20)
    n += 4
    img = [[[x / 100.0, y / 100.0, 0.0] for x in range(20)] for y in range(20)]
    mask = block(20, 20, 6, 6, 9, 9)
    crop, cmask, text = m.crop_by_mask(img, mask, 2, 4)
    inf = mm.parse_crop_info(text)
    assert (inf["w"], inf["h"]) == (8, 8) and len(crop) == 8 and len(crop[0]) == 8
    assert crop[0][0] == img[inf["y"]][inf["x"]] and sum(map(sum, cmask)) == 16
    assert raises(m.crop_by_mask, img, block(10, 10, 1, 1, 2, 2), 0, 1)  # size mismatch
    n += 4
    corner = block(20, 20, 0, 0, 1, 1)
    crop2, _, text2 = m.crop_by_mask(img, corner, 0, 8)
    i2 = mm.parse_crop_info(text2)
    assert (i2["x"], i2["y"], i2["w"]) == (0, 0, 8)
    n += 1
    # ---- paste back: round trip with an unchanged crop gives the original back
    for fe in (0, 3):
        back = m.paste_back(img, crop, None, text, fe)
        assert same(back, img)
        back = m.paste_back(img, crop, cmask, text, fe)
        assert same(back, img)
    n += 4
    # processed crop (all white) is blended in; centre solid, open edge fades
    white = solid(8, 8, 1.0)
    base = solid(20, 20, 0.0)
    out = m.paste_back(base, white, None, text, 0)
    assert out[inf["y"]][inf["x"]][0] == 1.0 and out[0][0][0] == 0.0
    soft = m.paste_back(base, white, None, text, 2)
    cy, cx = inf["y"] + 4, inf["x"] + 4
    assert soft[inf["y"]][inf["x"] + 4][0] < 1.0 and soft[cy][cx][0] == 1.0 and soft[0][0][0] == 0.0
    n += 3
    # crop touching the image border does not fade on that side
    cinfo = mm.make_crop_info((0, 0, 4, 4), 20, 20)
    b2 = m.paste_back(base, solid(4, 4, 1.0), None, cinfo, 2)
    assert b2[0][0][0] == 1.0 and b2[3][3][0] < 1.0
    n += 1
    # bigger processed crop is shrunk to the box
    up = m.paste_back(base, solid(16, 16, 1.0), None, text, 0)
    assert up[inf["y"]][inf["x"]][0] == 1.0
    n += 1
    # errors
    assert raises(m.paste_back, solid(10, 10, 0.0), crop, None, text, 0)  # wrong image size
    assert raises(m.paste_back, base, crop, None, text, -1)
    assert raises(m.paste_back, base, solid(8, 8, 1.0, 1), None, text, 0)  # fewer channels
    n += 3
    return n
