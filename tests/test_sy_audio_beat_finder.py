import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_audio_beat_finder as m


class _Fake:
    def __init__(self, shape):
        self.shape = shape


def _raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def _clicks(rate, seconds, every, first=0.0, length=5):
    s = [0.0] * int(rate * seconds)
    t = first
    while t < seconds:
        i = int(round(t * rate))
        for k in range(length):
            if i + k < len(s):
                s[i + k] = 0.9
        t += every
    return s


def run():
    n = 0
    rate = 1000
    # envelope: window of 20 ms = 20 samples
    env = m.energy_envelope([1.0] * 40 + [0.0] * 20, rate, 20)
    assert len(env) == 3 and abs(env[0] - 1.0) < 1e-9 and env[2] == 0.0; n += 1
    assert len(m.energy_envelope([0.5] * 25, rate, 20)) == 2; n += 1  # the short last window counts
    # click every 0.5 s starting at 0.0: four beats in 2 s (0.0, 0.5, 1.0, 1.5)
    track = _clicks(rate, 2.0, 0.5, first=0.0)
    env = m.energy_envelope(track, rate, 20)
    beats = m.find_beats(env, rate, 20, 0.5, 0.25, 1000)
    assert [round(b, 3) for b in beats] == [0.0, 0.5, 1.0, 1.5], beats; n += 1
    # clicks that start at 0.5 only: three beats
    track = _clicks(rate, 2.0, 0.5, first=0.5)
    beats = m.find_beats(m.energy_envelope(track, rate, 20), rate, 20, 0.5, 0.25, 1000)
    assert [round(b, 3) for b in beats] == [0.5, 1.0, 1.5], beats; n += 1
    # a long minimum gap merges close beats
    track = _clicks(rate, 2.0, 0.1, first=0.1)
    dense = m.find_beats(m.energy_envelope(track, rate, 20), rate, 20, 0.5, 0.05, 1000)
    sparse = m.find_beats(m.energy_envelope(track, rate, 20), rate, 20, 0.5, 0.5, 1000)
    assert len(sparse) < len(dense); n += 1
    # max_beats
    assert len(m.find_beats(env, rate, 20, 0.5, 0.25, 2)) == 2; n += 1
    # silence has no beats
    assert m.find_beats(m.energy_envelope([0.0] * 2000, rate, 20), rate, 20, 1.0, 0.25, 10) == []; n += 1
    # pure functions
    assert m.threshold_for(1.0) == 1.0 and m.threshold_for(0.0) == 1.0 + m.K; n += 1
    assert m.pick_peaks([], 2.0, 1) == []; n += 1
    assert m.pick_peaks([0.0, 1.0, 0.0, 0.0, 1.0, 0.0], 1.5, 1, 3) == [1, 4]; n += 1
    assert m.times_to_frames([0.0, 0.5, 1.51], 24) == [0, 12, 36]; n += 1
    assert _raises(m.times_to_frames, [1.0], 0); n += 1
    assert _raises(m.threshold_for, 1.5); n += 1
    assert _raises(m.energy_envelope, [0.1], 0, 20); n += 1
    assert _raises(m.energy_envelope, [0.1], 1000, 0); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 0)), "sample_rate": 44100}); n += 1
    assert m.SYAudioBeatFinder.RETURN_TYPES == ("STRING", "STRING", "INT"); n += 1
    assert m.SYAudioBeatFinder.CATEGORY == "SY/Audio"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYAudioBeatFinder"] == "Audio Beat Finder SY"; n += 1
    return n
