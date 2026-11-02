import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_audio_high_low_pass as m


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
    for order in (1, 2, 4):
        for kind in ("high", "low"):
            assert abs(m.butterworth_gain(500.0, 500.0, order, kind) - 0.70710678) < 1e-6; n += 1
    assert m.butterworth_gain(5.0, 500.0, 4, "high") < 1e-6; n += 1
    assert m.butterworth_gain(0.0, 500.0, 2, "high") == 0.0; n += 1
    assert m.butterworth_gain(1e-30, 500.0, 4, "high") < 1e-100; n += 1
    assert m.butterworth_gain(20000.0, 500.0, 4, "high") > 0.999; n += 1
    assert m.butterworth_gain(0.0, 500.0, 2, "low") == 1.0; n += 1
    assert m.butterworth_gain(20000.0, 500.0, 4, "low") < 1e-5; n += 1
    # steeper cuts more
    assert m.butterworth_gain(100.0, 500.0, 4, "high") < m.butterworth_gain(100.0, 500.0, 1, "high"); n += 1
    # high-pass rises with frequency, low-pass falls
    hp = [m.butterworth_gain(f, 500.0, 2, "high") for f in (50, 200, 500, 2000, 8000)]
    lp = [m.butterworth_gain(f, 500.0, 2, "low") for f in (50, 200, 500, 2000, 8000)]
    assert hp == sorted(hp) and lp == sorted(lp, reverse=True); n += 1
    assert all(0.0 <= g <= 1.0 for g in hp + lp); n += 1
    assert _raises(m.butterworth_gain, 100.0, 0.0, 2, "high"); n += 1
    assert _raises(m.butterworth_gain, 100.0, 100.0, 0, "high"); n += 1
    assert _raises(m.butterworth_gain, 100.0, 100.0, 2, "band"); n += 1
    m.check_cutoff(1000.0, 44100); n += 1
    assert _raises(m.check_cutoff, 22050.0, 44100); n += 1
    assert _raises(m.check_cutoff, 5000.0, 8000); n += 1
    assert _raises(m.check_cutoff, 0.0, 44100); n += 1
    assert m.SLOPES["gentle (6 dB)"] == 1 and m.SLOPES["normal (12 dB)"] == 2 and m.SLOPES["steep (24 dB)"] == 4; n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 0)), "sample_rate": 44100}); n += 1
    assert m.SYAudioHighLowPass.CATEGORY == "SY/Audio"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYAudioHighLowPass"] == "Audio High Low Pass SY"; n += 1
    return n
