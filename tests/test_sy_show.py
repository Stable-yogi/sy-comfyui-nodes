import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_show as m


class Fake:
    """Stands in for a tensor: only the shape matters here."""

    def __init__(self, *shape):
        self.shape = shape


def run():
    n = 0
    assert m.kind_of("hi") == "text" and m.kind_of(None) == "text"; n += 1
    assert m.kind_of(3) == "number" and m.kind_of(2.5) == "number" and m.kind_of(True) == "number"; n += 1
    assert m.kind_of([1, 2]) == "list"; n += 1
    assert m.kind_of({"samples": Fake(1, 4, 8, 8)}) == "latent"; n += 1
    assert m.kind_of({"waveform": Fake(1, 2, 100), "sample_rate": 10}) == "audio"; n += 1
    assert m.kind_of({"a": 1}) == "dict"; n += 1
    assert m.kind_of(Fake(2, 64, 48, 3)) == "image" and m.kind_of(Fake(1, 64, 48, 1)) == "image"; n += 1
    assert m.kind_of(Fake(1, 64, 48)) == "mask" and m.kind_of(Fake(64, 48)) == "mask"; n += 1
    assert m.kind_of(Fake(2, 3, 4, 5, 6)) == "tensor"; n += 1
    assert m.kind_of(object()) == "other"; n += 1
    assert m.pick_frames(0) == [] and m.pick_frames(3) == [0, 1, 2]; n += 1
    pf = m.pick_frames(100)
    assert pf[0] == 0 and pf[-1] == 99 and len(pf) == m.MAX_PICTURES; n += 1
    assert m.describe("abc") == "abc" and m.describe(None) == "" and m.describe(7) == "7"; n += 1
    assert m.describe(["a", 2]) == "a\n2"; n += 1
    assert m.describe(Fake(9, 480, 832, 3)) == "Picture: 9 frame(s), 832x480, 3 channel(s)"; n += 1
    assert m.describe(Fake(1, 4, 5)) == "Mask: 1x4x5"; n += 1
    assert m.describe({"samples": Fake(1, 16, 3, 60, 104)}) == "Latent: shape 1x16x3x60x104"; n += 1
    assert m.describe({"waveform": Fake(1, 2, 96000), "sample_rate": 48000}) == "Sound: 2.00 s, 2 channel(s), 48000 Hz"; n += 1
    assert m.describe({"a": 1}).startswith("{"); n += 1
    assert m.clip_text("x" * 5, 10) == "x" * 5 and "5 more characters" in m.clip_text("x" * 15, 10); n += 1
    assert m.SYShow.OUTPUT_NODE is True and m.SYShow.RETURN_NAMES == ("value",); n += 1
    return n
