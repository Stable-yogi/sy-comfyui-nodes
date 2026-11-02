import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_audio_mix as m


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
    assert m.mix_plan(100, 50, 0, "longest") == (100, 0); n += 1
    assert m.mix_plan(100, 50, 80, "longest") == (130, 80); n += 1
    assert m.mix_plan(100, 50, 80, "length of A") == (100, 80); n += 1
    assert m.mix_plan(100, 50, 80, "length of B placed") == (130, 80); n += 1
    assert m.mix_plan(100, 50, 500, "length of A") == (100, 500); n += 1
    assert _raises(m.mix_plan, 0, 5, 0, "longest"); n += 1
    assert _raises(m.mix_plan, 5, 5, -1, "longest"); n += 1
    assert _raises(m.mix_plan, 5, 5, 0, "shortest"); n += 1
    assert m.batch_for(1, 1) == 1 and m.batch_for(3, 1) == 3 and m.batch_for(1, 3) == 3 and m.batch_for(2, 2) == 2; n += 1
    assert _raises(m.batch_for, 2, 3); n += 1
    assert m.clip_scale(2.0, True) == 0.5; n += 1
    assert m.clip_scale(0.9, True) == 1.0; n += 1
    assert m.clip_scale(2.0, False) == 1.0; n += 1
    ok = {"waveform": _Fake((1, 2, 10)), "sample_rate": 44100}
    assert m.check_audio(ok) == (1, 2, 10, 44100); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 6, 10)), "sample_rate": 44100}, "audio_b"); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 0)), "sample_rate": 44100}); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 10)), "sample_rate": 0}); n += 1
    assert m.SYAudioMix.CATEGORY == "SY/Audio"; n += 1
    return n
