import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_audio_speed_change as m


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
    assert m.new_length(1000, 2.0) == 500; n += 1
    assert m.new_length(1000, 0.5) == 2000; n += 1
    assert m.new_length(1000, 1.0) == 1000; n += 1
    assert m.new_length(1, 4.0) == 1; n += 1
    assert m.new_length(3, 4.0) == 1; n += 1
    assert _raises(m.new_length, 100, 0); n += 1
    assert _raises(m.new_length, 0, 1.0); n += 1
    ramp = [float(i) for i in range(10)]
    assert m.interpolate_at(ramp, 2.5, "linear") == 2.5; n += 1
    assert abs(m.interpolate_at(ramp, 2.5, "cubic") - 2.5) < 1e-9; n += 1  # a straight line stays straight
    assert m.interpolate_at(ramp, 3.0, "cubic") == 3.0; n += 1
    assert m.interpolate_at(ramp, -5, "linear") == 0.0 and m.interpolate_at(ramp, 99, "cubic") == 9.0; n += 1
    # speed 1 gives an identical copy
    assert m.resample_list(ramp, 1.0, "linear") == ramp; n += 1
    assert m.resample_list(ramp, 1.0, "cubic") == ramp; n += 1
    # speed 2 halves, speed 0.5 doubles
    assert len(m.resample_list(ramp, 2.0, "linear")) == 5; n += 1
    assert m.resample_list(ramp, 2.0, "linear") == [0.0, 2.0, 4.0, 6.0, 8.0]; n += 1
    assert len(m.resample_list(ramp, 0.5, "cubic")) == 20; n += 1
    assert m.resample_list(ramp, 0.5, "linear")[:3] == [0.0, 0.5, 1.0]; n += 1
    assert _raises(m.interpolate_at, ramp, 1.0, "nearest"); n += 1
    assert _raises(m.interpolate_at, [], 0.0, "linear"); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 0)), "sample_rate": 44100}); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 5)), "sample_rate": 0}); n += 1
    assert m.SYAudioSpeedChange.RETURN_TYPES == ("AUDIO", "FLOAT"); n += 1
    assert m.SYAudioSpeedChange.CATEGORY == "SY/Audio"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYAudioSpeedChange"] == "Audio Speed Change SY"; n += 1
    return n
