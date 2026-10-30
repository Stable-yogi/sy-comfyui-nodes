import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_group_switch as m


def run():
    n = 0
    assert m.visible_groups(["A", "Upscale", "upscale 2"], "") == ["A", "Upscale", "upscale 2"]; n += 1
    assert m.visible_groups(["A", "Upscale", "upscale 2"], "UPS") == ["Upscale", "upscale 2"]; n += 1
    assert m.visible_groups(["A"], None) == ["A"]; n += 1
    assert m.visible_groups([], "x") == []; n += 1
    t = ["a", "b", "c"]
    assert m.next_states(t, [True, True, False], 2, True) == [True, True, True]; n += 1
    assert m.next_states(t, [True, True, False], 0, False) == [False, True, False]; n += 1
    assert m.next_states(t, [True, True, False], 2, True, exclusive=True) == [False, False, True]; n += 1
    assert m.next_states(t, [True, True, False], 0, False, exclusive=True) == [False, True, False]; n += 1
    states = [True, False, True]
    m.next_states(t, states, 1, True)
    assert states == [True, False, True]; n += 1  # input list is not changed
    for bad in ((t, [True], 0, True), (t, [True, True, True], 3, True), (t, [True, True, True], -1, True)):
        try:
            m.next_states(*bad)
        except ValueError:
            n += 1
        else:
            raise AssertionError("expected ValueError")
    assert m.SYGroupSwitch().run() == (); n += 1
    assert m.SYGroupSwitch.RETURN_TYPES == (); n += 1
    return n
