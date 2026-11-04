import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_voice_split as m


def run():
    n = 0
    levels = [1.0] * 200          # 10 s at 0.05 s windows
    levels[110] = 0.0             # a pause at 5.5 s
    cuts, notes = m.plan_cuts(levels, 0.05, 2, 1.0)
    assert cuts == [5.5] and notes == [], (cuts, notes); n += 1
    cuts, _ = m.plan_cuts(levels, 0.05, 2, 0.25)
    assert cuts == [5.0], cuts; n += 1          # pause out of reach: even point
    cuts, _ = m.plan_cuts([1.0] * 200, 0.05, 4, 2.0)
    assert cuts == [2.5, 5.0, 7.5], cuts; n += 1
    assert m.plan_cuts([1.0] * 200, 0.05, 1)[0] == []; n += 1
    _, notes = m.plan_cuts([1.0] * 800, 0.05, 2)
    assert notes and "piece 1 is 20.0 s" in notes[0], notes; n += 1
    for bad in (([], 0.05, 2), ([1.0] * 10, 0.05, 2), ([1.0] * 200, 0.05, 0), ([1.0] * 200, 0.05, 7),
                ([1.0] * 200, 0.05, 2, -1)):
        try:
            m.plan_cuts(*bad)
            raise SystemExit("bad input must raise: %r" % (bad,))
        except ValueError:
            n += 1
    r = m.piece_ranges([5.0, 9.0], 12.0, 1.625)
    assert r == [(0.0, 5.0), (3.375, 9.0), (7.375, 12.0)], r; n += 1
    assert m.piece_ranges([], 3.0) == [(0.0, 3.0)]; n += 1
    try:
        m.piece_ranges([1.0], 3.0, -0.5)
        raise SystemExit("negative overlap must raise")
    except ValueError:
        n += 1
    try:
        import torch
    except ImportError:
        return n
    rate = 1000
    wave = torch.ones(1, 1, 10 * rate) * 0.5
    wave[..., 5500:5550] = 0.0
    lv = m.window_levels(wave[0], rate)
    assert len(lv) == 200 and lv[110] == 0.0, len(lv); n += 1
    out = m.SYVoiceSplit().run({"waveform": wave, "sample_rate": rate}, 2, 1.0, 1.0)
    p1, p2 = out[0], out[1]
    assert p1["waveform"].shape[-1] == 5500 and p2["waveform"].shape[-1] == 5500, (p1["waveform"].shape, p2["waveform"].shape); n += 1
    assert out[6] == "5.500, 5.500" and out[7] == 2 and "cuts at 5.50" in out[8], out[6:]; n += 1
    assert out[5]["waveform"].shape[-1] == 100 and float(out[5]["waveform"].abs().sum()) == 0.0; n += 1
    try:
        m.SYVoiceSplit().run({"waveform": torch.ones(1, 1, 500), "sample_rate": rate}, 2)
        raise SystemExit("too short must raise")
    except ValueError:
        n += 1
    return n
