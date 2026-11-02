import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_audio_loop_to_length as m


class _Fake:
    def __init__(self, shape):
        self.shape = shape


def _raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def _covered(plan, target):
    """Painted length: every sample 0..target-1 must be written by some segment."""
    cover = [False] * target
    for s0, s1, d0, _f in plan:
        for i in range(d0, d0 + (s1 - s0)):
            assert i < target
            cover[i] = True
    return all(cover)


def run():
    n = 0
    # shorter target: one cut segment
    assert m.loop_plan(100, 40, 10) == [(0, 40, 0, 0)]; n += 1
    assert m.loop_plan(100, 100, 10) == [(0, 100, 0, 0)]; n += 1
    # no crossfade: plain repeats
    assert m.loop_plan(100, 250, 0) == [(0, 100, 0, 0), (0, 100, 100, 0), (0, 50, 200, 0)]; n += 1
    # crossfade 10: each repeat starts 90 later and blends 10
    p = m.loop_plan(100, 250, 10)
    assert p[0] == (0, 100, 0, 0) and p[1] == (0, 100, 90, 10) and p[2] == (0, 70, 180, 10), p; n += 1
    # crossfade is limited to half the clip
    p = m.loop_plan(100, 250, 999)
    assert all(seg[3] <= 50 for seg in p); n += 1
    assert p[1][2] == 50; n += 1
    # the plan always fills the exact length
    for clip in (1, 2, 7, 100):
        for target in (1, 5, 99, 100, 101, 357, 1000):
            for cf in (0, 1, 3, 40, 500):
                plan = m.loop_plan(clip, target, cf)
                assert _covered(plan, target), (clip, target, cf, plan)
                last = plan[-1]
                assert last[2] + (last[1] - last[0]) == target, (clip, target, cf, plan)
                for seg in plan[1:]:
                    assert seg[1] - seg[0] > seg[3]
    n += 1
    assert m.final_fade_len(10000, 100) == 100; n += 1
    assert m.final_fade_len(100, 100) == 50; n += 1
    assert _raises(m.loop_plan, 0, 10, 0); n += 1
    assert _raises(m.loop_plan, 10, 0, 0); n += 1
    assert _raises(m.loop_plan, 10, 10, -1); n += 1
    assert _raises(m.check_audio, {"waveform": _Fake((1, 2, 0)), "sample_rate": 44100}); n += 1
    assert m.SYAudioLoopToLength.CATEGORY == "SY/Audio"; n += 1
    return n
