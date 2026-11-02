import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_audio_fade as m


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
    # linear fade in
    assert m.fade_gain(0.0, 10, 2, 0, "linear") == 0.0; n += 1
    assert abs(m.fade_gain(1.0, 10, 2, 0, "linear") - 0.5) < 1e-9; n += 1
    assert m.fade_gain(5.0, 10, 2, 2, "linear") == 1.0; n += 1
    # fade out reaches silence at the end
    assert abs(m.fade_gain(10.0, 10, 0, 2, "linear")) < 1e-9; n += 1
    assert abs(m.fade_gain(9.0, 10, 0, 2, "linear") - 0.5) < 1e-9; n += 1
    # smooth is 0.5 in the middle, exponential is below linear in the middle
    assert abs(m.fade_gain(1.0, 10, 2, 0, "smooth") - 0.5) < 1e-9; n += 1
    assert m.fade_gain(1.0, 10, 2, 0, "exponential") < 0.5; n += 1
    # overlapping fades shrink in proportion (3 + 1 on a 2 s clip -> 1.5 and 0.5)
    fi, fo = m.effective_fades(2.0, 3.0, 1.0)
    assert abs(fi - 1.5) < 1e-9 and abs(fo - 0.5) < 1e-9; n += 1
    # a fade longer than the clip is limited to the clip
    fi, fo = m.effective_fades(2.0, 50.0, 0.0)
    assert fi == 2.0 and fo == 0.0; n += 1
    # gain always in 0..1
    for c in m.CURVES:
        for i in range(0, 41):
            g = m.fade_gain(i * 0.05, 2.0, 1.5, 1.5, c)
            assert 0.0 <= g <= 1.0
    n += 1
    # regions: first sample silent, last sample silent
    head, tail_start, tail = m.fade_regions(1000, 100, 1.0, 1.0, "linear")
    assert head[0] == 0.0 and tail[-1] == 0.0 and tail_start + len(tail) == 1000; n += 1
    # no fades -> no regions
    head, tail_start, tail = m.fade_regions(1000, 100, 0.0, 0.0, "smooth")
    assert head == [] and tail == []; n += 1
    # errors
    assert _raises(m.fade_gain, 1.0, 10, 1, 1, "wobble"); n += 1
    assert _raises(m.effective_fades, 10, -1, 0); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 0)), "sample_rate": 44100}); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 10)), "sample_rate": 0}); n += 1
    assert _raises(m.check_audio, "nope"); n += 1
    assert m.check_audio({"waveform": _Fake((1, 2, 10)), "sample_rate": 44100}) == (1, 2, 10, 44100); n += 1
    assert m.SYAudioFade.RETURN_TYPES == ("AUDIO",); n += 1
    assert m.SYAudioFade.CATEGORY == "SY/Audio"; n += 1
    return n
