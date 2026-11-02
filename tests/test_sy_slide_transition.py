import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_slide_transition as m


def _raises(call, text):
    try:
        call()
    except ValueError as e:
        assert text in str(e), str(e)
        return 1
    raise SystemExit("expected ValueError: " + text)


def run():
    n = 0
    ps = [m.transition_progress(i, 12) for i in range(12)]
    assert all(0.0 < p < 1.0 for p in ps); n += 1
    assert all(ps[i] < ps[i + 1] for i in range(11)); n += 1
    assert abs(m.transition_progress(0, 1) - 0.5) < 1e-9; n += 1       # middle of the ease
    assert ps[0] < 1.0 / 13 and ps[-1] > 12.0 / 13; n += 1             # eased at both ends
    al = m.wipe_alpha(10, 0.0, 0.05)
    assert al == [0.0] * 10; n += 1
    assert m.wipe_alpha(10, 1.0, 0.05) == [1.0] * 10; n += 1
    assert m.wipe_alpha(10, 1.0, 0.0) == [1.0] * 10; n += 1
    assert m.wipe_alpha(4, 0.5, 0.0) == [1.0, 1.0, 0.0, 0.0]; n += 1
    soft = m.wipe_alpha(20, 0.5, 0.5)
    assert all(soft[i] >= soft[i + 1] for i in range(19)) and 0.0 < soft[10] < 1.0; n += 1
    assert m.wipe_alpha(1, 1.0, 0.1) == [1.0]; n += 1
    assert m.join_plan(30, 20, 12) == (18, 8, 38); n += 1
    assert m.join_plan(2, 2, 2) == (0, 0, 2); n += 1
    assert m.join_plan(200, 200, 120) == (80, 80, 280); n += 1
    n += _raises(lambda: m.join_plan(5, 20, 12), "clip A has only 5 frames")
    n += _raises(lambda: m.join_plan(20, 5, 12), "clip B has only 5 frames")
    n += _raises(lambda: m.join_plan(20, 20, 1), "between 2 and 120")
    n += _raises(lambda: m.transition_progress(12, 12), "index must be from 0 to 11")
    n += _raises(lambda: m.transition_progress(0, 0), "at least 1")
    n += _raises(lambda: m.wipe_alpha(0, 0.5, 0.1), "at least 1")
    n += _raises(lambda: m.wipe_alpha(4, 1.5, 0.1), "between 0 and 1")
    n += _raises(lambda: m.wipe_alpha(4, 0.5, 0.9), "between 0 and 0.5")
    assert len(m.STYLES) == 6 and m.SYSlideTransition.RETURN_TYPES == ("IMAGE",); n += 1
    return n
