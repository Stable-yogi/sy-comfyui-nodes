import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_audio_gain_db as m


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
    assert m.db_to_gain(0) == 1.0; n += 1
    assert abs(m.db_to_gain(6.0206) - 2.0) < 1e-3; n += 1
    assert abs(m.db_to_gain(-20) - 0.1) < 1e-9; n += 1
    assert abs(m.gain_to_db(0.5) - (-6.0206)) < 1e-3; n += 1
    assert m.gain_to_db(0) == -120.0; n += 1
    assert m.gain_to_db(1e-9) == -120.0; n += 1
    assert abs(m.gain_to_db(m.db_to_gain(-17.3)) - (-17.3)) < 1e-9; n += 1
    # soft limit: odd, rising, below 1, identity for small values
    assert m.soft_limit(0.0) == 0.0; n += 1
    assert m.soft_limit(0.3) == 0.3 and m.soft_limit(-0.3) == -0.3; n += 1
    prev = -1.0
    for i in range(0, 60):
        x = i * 0.05
        y = m.soft_limit(x)
        assert y >= prev and y < 1.0 and abs(m.soft_limit(-x) + y) < 1e-12
        prev = y
    n += 1
    assert 0.99 < m.soft_limit(50.0) <= 1.0; n += 1
    # continuous at the knee
    assert abs(m.soft_limit(0.5 + 1e-9) - 0.5) < 1e-6; n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 0)), "sample_rate": 44100}); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 10)), "sample_rate": 0}); n += 1
    assert _raises(m.check_audio, 5); n += 1
    assert m.SYAudioGainDb.RETURN_TYPES == ("AUDIO", "FLOAT"); n += 1
    assert m.SYAudioGainDb.CATEGORY == "SY/Audio"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYAudioGainDb"] == "Audio Gain dB SY"; n += 1
    return n
