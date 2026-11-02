import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_audio_reverse as m


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
    a = [0.1, 0.5, -0.3, 0.9, 0.0]
    assert m.reverse_list(a) == [0.0, 0.9, -0.3, 0.5, 0.1]; n += 1
    assert m.reverse_list(m.reverse_list(a)) == a; n += 1
    assert m.reverse_list([]) == []; n += 1
    assert a == [0.1, 0.5, -0.3, 0.9, 0.0]; n += 1  # input not changed
    assert _raises(m.check_audio, {"waveform": _Fake((1, 1, 0)), "sample_rate": 44100}); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 1, 4)), "sample_rate": -1}); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((2, 4)), "sample_rate": 44100}); n += 1
    assert m.check_audio({"waveform": _Fake((1, 1, 4)), "sample_rate": 8000}) == (1, 1, 4, 8000); n += 1
    assert m.SYAudioReverse.RETURN_TYPES == ("AUDIO",); n += 1
    assert m.SYAudioReverse.CATEGORY == "SY/Audio"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYAudioReverse"] == "Audio Reverse SY"; n += 1
    return n
