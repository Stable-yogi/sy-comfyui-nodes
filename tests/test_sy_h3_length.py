import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_length as m


def run():
    n = 0
    f, r, info = m.frames_for(5.0, 24, "up")
    assert f == 124 and f % 17 == 5, f; n += 1  # 120 wanted -> 17*7+5
    assert r == round(124 / 24.0, 3); n += 1
    assert m.frames_for(0.1, 24, "up")[0] == 5; n += 1  # never below 5
    assert m.frames_for(0.1, 24, "down")[0] == 5; n += 1
    assert m.frames_for(10.0, 24, "up")[0] == 243, m.frames_for(10.0, 24, "up"); n += 1  # 240 -> 17*14+5
    assert m.frames_for(10.0, 24, "down")[0] == 226; n += 1
    assert m.frames_for(10.0, 24, "nearest")[0] == 243; n += 1
    assert m.frames_for(15.0, 24, "up")[0] == 362; n += 1  # top of the trained range
    for sec in (0.5, 1, 2.2, 7.7, 30):
        for mode in m.ROUNDS:
            assert m.frames_for(sec, 24, mode)[0] % 17 == 5; n += 1
    assert m.frames_for(1.0, 24, "up")[0] == 39 and m.frames_for(1.0, 24, "down")[0] == 22; n += 1
    assert "frames" in m.frames_for(2, 24)[2]; n += 1
    for bad in ((0, 24, "up"), (-1, 24, "up"), (2, 0, "up"), (2, 24, "left")):
        try:
            m.frames_for(*bad)
        except ValueError:
            n += 1
        else:
            raise AssertionError("expected ValueError for %r" % (bad,))
    assert m.SYH3Length.RETURN_TYPES == ("INT", "FLOAT", "STRING"); n += 1
    return n
