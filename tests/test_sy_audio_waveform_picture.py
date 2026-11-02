import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_audio_waveform_picture as m


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
    ext = m.column_extremes([0.0, 1.0, -1.0, 0.5, 0.25, -0.25], 3)
    assert ext == [(0.0, 1.0), (-1.0, 0.5), (-0.25, 0.25)], ext; n += 1
    assert len(m.column_extremes([0.1] * 1000, 64)) == 64; n += 1
    assert len(m.column_extremes([0.1, 0.2], 8)) == 8; n += 1  # more columns than samples
    assert m.column_extremes([0.1, 0.2], 4)[0] == (0.1, 0.1); n += 1
    uneven = m.column_extremes(list(range(10)), 3)  # chunks of 3, 3, 4
    assert uneven == [(0, 2), (3, 5), (6, 9)], uneven; n += 1
    assert _raises(m.column_extremes, [], 4); n += 1
    assert _raises(m.column_extremes, [0.1], 0); n += 1
    assert m.value_to_row(0.0, 101) == 50 and m.value_to_row(1.0, 101) == 0 and m.value_to_row(-1.0, 101) == 100; n += 1
    assert m.value_to_row(5.0, 101) == 0; n += 1
    # silence: one row in the centre per column
    rows = m.column_rows(m.column_extremes([0.0] * 100, 10), 101)
    assert all(t == b == 50 for t, b in rows); n += 1
    assert m.column_rows([(-1.0, 1.0)], 101) == [(0, 100)]; n += 1
    assert _raises(m.column_rows, [(0, 0)], 0); n += 1
    # bars: width 40 gives 10 bars of 3 pixels with a 1 pixel gap
    be = m.bar_extremes([0.5] * 100 + [-0.25] * 100, 40)
    assert len(be) == 40 and be[0] == (-0.5, 0.5) and be[3] == (0.0, 0.0); n += 1
    assert m.bar_gaps(40) == set(range(3, 40, 4)); n += 1
    assert m.bar_gaps(2) == set(); n += 1
    # layout of stacked channels
    assert m.band_layout(100, 2) == [(0, 50), (50, 50)]; n += 1
    assert m.band_layout(101, 2) == [(0, 50), (50, 51)]; n += 1
    assert _raises(m.band_layout, 3, 2); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 0)), "sample_rate": 44100}); n += 1
    assert m.SYAudioWaveformPicture.RETURN_TYPES == ("IMAGE",); n += 1
    assert m.SYAudioWaveformPicture.CATEGORY == "SY/Audio"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYAudioWaveformPicture"] == "Audio Waveform Picture SY"; n += 1
    return n
