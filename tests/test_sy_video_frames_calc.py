import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_video_frames_calc as m


def _raises(*args):
    try:
        m.calc_frames(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.calc_frames(5, 16, False) == (80, 16.0, 5.0); n += 1
    assert m.calc_frames(5, 16, True) == (81, 16.0, 81 / 16); n += 1
    assert m.calc_frames(1, 24, False)[0] == 24; n += 1
    assert m.calc_frames(1, 24, True)[0] == 25; n += 1
    assert m.calc_frames(10, 24, True)[0] == 241; n += 1
    assert m.calc_frames(0.01, 1, False)[0] == 1; n += 1  # tiny still gives one frame
    assert m.calc_frames(0.01, 1, True)[0] == 1; n += 1
    assert m.calc_frames(0.1, 24, True)[0] == 1; n += 1  # 2 frames -> nearest 4n+1 is 1
    assert m.calc_frames(0.2, 24, True)[0] == 5; n += 1
    for secs in (0.37, 1.5, 3.3, 7.77, 60):
        f = m.calc_frames(secs, 24, True)[0]
        assert (f - 1) % 4 == 0 and f >= 1; n += 1
    assert m.calc_frames(2.5, 30, False)[2] == 75 / 30; n += 1  # real seconds from the frame count
    assert m.calc_frames(3600, 60, False)[0] == 216000; n += 1  # huge but legal
    for bad in ((0, 24, False), (-1, 24, False), (5, 0, False), (5, -3, True), (5, float("nan"), True),
                (float("inf"), 24, True), (100000, 1000, False)):
        assert _raises(*bad), bad
        n += 1
    assert m.SYVideoFramesCalc().run(5, 16, True)[0] == 81; n += 1
    return n
