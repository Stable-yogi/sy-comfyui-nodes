import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_colour_contrast_check as m


def run():
    n = 0
    k, w = (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)
    assert abs(m.contrast_ratio(k, w) - 21.0) < 1e-9; n += 1
    assert abs(m.contrast_ratio(w, k) - 21.0) < 1e-9; n += 1
    assert m.contrast_ratio((0.3, 0.5, 0.7), (0.3, 0.5, 0.7)) == 1.0; n += 1
    assert abs(m.contrast_ratio((0.5, 0.5, 0.5), w) - 3.9767) < 0.001; n += 1
    assert m.grade_for(1.0) == "poor" and m.grade_for(2.99) == "poor"; n += 1
    assert m.grade_for(3.0) == "ok for large text" and m.grade_for(4.49) == "ok for large text"; n += 1
    assert m.grade_for(4.5) == "good" and m.grade_for(6.99) == "good"; n += 1
    assert m.grade_for(7.0) == "great" and m.grade_for(21.0) == "great"; n += 1
    r, g, b = m.check_contrast("fff", "000")
    assert abs(r - 21.0) < 1e-9 and g == "great" and b == "#ffffff"; n += 1
    r, g, b = m.check_contrast("#ffffff", "#ffff00")
    assert g == "poor" and b == "#000000"; n += 1
    r, g, b = m.check_contrast("777", "888")
    assert g == "poor"; n += 1
    assert m.check_contrast("000", "808080")[2] == "#000000"; n += 1
    assert m.check_contrast("fff", "202020")[2] == "#ffffff"; n += 1
    for args, word in ((("zz", "000"), "foreground"), (("000", "12"), "background")):
        try:
            m.check_contrast(*args)
            raise SystemExit("bad hex must raise")
        except ValueError as e:
            assert word in str(e), str(e)
            n += 1
    out = m.SYColourContrastCheck().run("000000", "ffffff")
    assert out[1] == "great" and out[2] == "#000000"; n += 1
    return n
