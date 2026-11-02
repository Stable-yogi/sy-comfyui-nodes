import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_audio_info as m


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
    assert m.channel_name(1) == "mono" and m.channel_name(2) == "stereo"; n += 1
    assert m.channel_name(6) == "6 channels"; n += 1
    assert _raises(m.channel_name, 0); n += 1
    assert m.format_report(2.0, 44100, 2, -3.0, -9.2) == "2.00 s, 44100 Hz, stereo, peak -3.0 dB, average -9.2 dB"; n += 1
    assert m.format_report(0.5, 8000, 1, -120.0, -120.0) == "0.50 s, 8000 Hz, mono, peak -120.0 dB, average -120.0 dB"; n += 1
    assert m.level_to_db(0.0) == -120.0; n += 1
    assert m.level_to_db(1.0) == 0.0; n += 1
    assert abs(m.level_to_db(0.5) + 6.0206) < 1e-3; n += 1
    assert m.stats_of_list([0.0, 0.0, 0.0]) == (-120.0, -120.0); n += 1
    peak, rms = m.stats_of_list([0.5, -0.5, 0.5, -0.5])
    assert abs(peak - rms) < 1e-9 and abs(peak + 6.0206) < 1e-3; n += 1
    assert _raises(m.stats_of_list, []); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 0)), "sample_rate": 44100}); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 5)), "sample_rate": 0}); n += 1
    assert m.SYAudioInfo.RETURN_NAMES[-1] == "report" and len(m.SYAudioInfo.RETURN_TYPES) == 7; n += 1
    assert m.SYAudioInfo.CATEGORY == "SY/Audio"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYAudioInfo"] == "Audio Info SY"; n += 1
    return n
