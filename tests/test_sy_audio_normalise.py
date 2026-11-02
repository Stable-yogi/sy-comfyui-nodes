import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_audio_normalise as m


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
    # peak 0.5 -> -1 dB target: gain = -1 + 6.0206 = 5.0206
    assert abs(m.gain_for(0.5, -1.0, 30) - (-1.0 + 20 * math.log10(2))) < 1e-9; n += 1
    # gain is limited
    assert m.gain_for(0.001, 0.0, 30) == 30; n += 1
    # loud audio is turned down (negative gain)
    assert m.gain_for(1.0, -6.0, 30) == -6.0; n += 1
    # silent audio: no gain
    assert m.gain_for(0.0, -1.0, 30) == 0.0; n += 1
    # peak mode never clips: applying the gain puts the peak at the target
    peak = 0.25
    g = m.gain_for(peak, -1.0, 30)
    assert peak * 10 ** (g / 20) <= 1.0; n += 1
    assert abs(peak * 10 ** (g / 20) - 10 ** (-1.0 / 20)) < 1e-9; n += 1
    # measures
    assert m.peak_of([0.1, -0.7, 0.3]) == 0.7; n += 1
    assert m.peak_of([]) == 0.0; n += 1
    assert abs(m.rms_of([1.0, -1.0, 1.0, -1.0]) - 1.0) < 1e-12; n += 1
    assert m.rms_of([]) == 0.0; n += 1
    assert _raises(m.gain_for, -0.1, -1, 30); n += 1
    assert _raises(m.gain_for, 0.5, -1, -3); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 1, 0)), "sample_rate": 44100}); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 1, 5)), "sample_rate": -1}); n += 1
    assert m.SYAudioNormalise.RETURN_NAMES == ("audio", "gain_db"); n += 1
    assert m.SYAudioNormalise.CATEGORY == "SY/Audio"; n += 1
    return n
