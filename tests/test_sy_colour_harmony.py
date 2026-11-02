import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_colour_harmony as m


def run():
    n = 0
    hh = m.harmony_hues
    assert hh(0, "complementary") == [0.0, 180.0]; n += 1
    assert hh(30, "triad") == [30.0, 150.0, 270.0]; n += 1
    assert hh(300, "triad") == [300.0, 60.0, 180.0]; n += 1   # wraps past 360
    assert hh(10, "tetrad") == [10.0, 100.0, 190.0, 280.0]; n += 1
    assert hh(100, "analogous", 30) == [100.0, 70.0, 130.0]; n += 1
    assert hh(10, "analogous", 60) == [10.0, 310.0, 70.0]; n += 1
    assert hh(0, "split complementary", 30) == [0.0, 150.0, 210.0]; n += 1
    assert hh(0, "split complementary", 10) == [0.0, 170.0, 190.0]; n += 1
    red = m.harmony_palette("f00", "complementary")
    assert red == ["#ff0000", "#00ffff"], red; n += 1
    assert m.harmony_palette("#ff0000", "triad") == ["#ff0000", "#00ff00", "#0000ff"]; n += 1
    assert m.harmony_palette("808080", "tetrad") == ["#808080"] * 4; n += 1   # grey has no hue to move
    assert len(m.harmony_palette("3366cc", "analogous", 20)) == 3; n += 1
    for call, word in ((lambda: hh(0, "square"), "scheme must be"), (lambda: hh(0, "triad", 5), "spread must be"),
                       (lambda: hh(0, "triad", 61), "spread must be"), (lambda: m.harmony_palette("zzz"), "hex digits")):
        try:
            call()
            raise SystemExit("bad input must raise")
        except ValueError as e:
            assert word in str(e), str(e)
            n += 1
    out = m.SYColourHarmony().run("ff0000", "complementary", 30.0)
    assert out == ("#ff0000,#00ffff", 2); n += 1
    return n
