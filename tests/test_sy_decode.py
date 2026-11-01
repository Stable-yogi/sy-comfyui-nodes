import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_decode as m


def must_raise(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected a ValueError")


def run():
    n = 0
    assert m.tile_ladder(512) == [512, 256, 128, 64]; n += 1
    assert m.tile_ladder(64) == [64]; n += 1
    assert m.tile_ladder(300) == [300, 150, 75]; n += 1
    assert "at least" in must_raise(m.tile_ladder, 32); n += 1
    assert m.plan_decode("Picture or video", "Never tiles", 512) == [(False, 0)]; n += 1
    assert m.plan_decode("Picture or video", "Always tiles", 256) == [(True, 256), (True, 128), (True, 64)]; n += 1
    auto = m.plan_decode("Sound", "Auto (retry in tiles)", 128)
    assert auto[0] == (False, 0) and auto[1:] == [(True, 128), (True, 64)]; n += 1
    assert "mode" in must_raise(m.plan_decode, "Movie", "Never tiles", 512); n += 1
    assert "tiles" in must_raise(m.plan_decode, "Sound", "Sometimes", 512); n += 1
    assert m.info_text("Sound", 1, (False, 0), "2.00 s at 44100 Hz") == "Sound: 2.00 s at 44100 Hz, in one piece"; n += 1
    t = m.info_text("Picture or video", 3, (True, 256), "9 frame(s) of 832x480")
    assert "tiles of 256" in t and "3 tries" in t; n += 1
    assert m.SYDecode.RETURN_NAMES == ("image", "audio", "info"); n += 1
    spec = m.SYDecode.INPUT_TYPES()["required"]
    assert spec["mode"][0] == m.MODES and spec["tiles"][0] == m.TILED; n += 1
    return n
