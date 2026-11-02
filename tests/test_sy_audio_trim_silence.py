import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_audio_trim_silence as m


class _Fake:
    def __init__(self, shape):
        self.shape = shape


def _raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    # windows of 10 samples, loud in windows 3..5 of 10
    lv = [0, 0, 0, 1, 1, 1, 0, 0, 0, 0]
    assert m.find_keep_range(lv, 0.5, 0, "both", 10, 100) == (30, 60); n += 1
    assert m.find_keep_range(lv, 0.5, 5, "both", 10, 100) == (25, 65); n += 1
    assert m.find_keep_range(lv, 0.5, 0, "start", 10, 100) == (30, 100); n += 1
    assert m.find_keep_range(lv, 0.5, 0, "end", 10, 100) == (0, 60); n += 1
    # padding is limited to the clip
    assert m.find_keep_range(lv, 0.5, 500, "both", 10, 100) == (0, 100); n += 1
    # the level must pass the threshold
    assert m.find_keep_range([0.5, 0.5], 0.5, 0, "both", 10, 20) == (0, 0); n += 1
    # all silent
    assert m.find_keep_range([0, 0, 0], 0.5, 0, "both", 10, 30) == (0, 0); n += 1
    assert m.find_keep_range([], 0.5, 0, "both", 10, 0) == (0, 0); n += 1
    # default total from levels
    assert m.find_keep_range(lv, 0.5, 0, "start", 10) == (30, 100); n += 1
    # minimum keep
    assert m.enforce_min_keep(0, 0, 1000, 100, True) == (0, 100); n += 1
    assert m.enforce_min_keep(30, 40, 1000, 100, False) == (30, 130); n += 1
    assert m.enforce_min_keep(950, 960, 1000, 100, False) == (900, 1000); n += 1
    assert m.enforce_min_keep(30, 400, 1000, 100, False) == (30, 400); n += 1
    assert m.enforce_min_keep(0, 0, 50, 100, True) == (0, 50); n += 1
    # errors
    assert _raises(m.find_keep_range, [1], 0.5, 0, "middle"); n += 1
    assert _raises(m.find_keep_range, [1], 0.5, -1, "both"); n += 1
    assert _raises(m.find_keep_range, [1], 0.5, 0, "both", 0); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 0)), "sample_rate": 44100}); n += 1
    assert m.SYAudioTrimSilence.RETURN_TYPES == ("AUDIO", "FLOAT"); n += 1
    assert m.SYAudioTrimSilence.CATEGORY == "SY/Audio"; n += 1
    return n
