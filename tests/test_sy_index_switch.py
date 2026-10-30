import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_index_switch as m


def _raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    vals = ["a", "b", "c", "d"]
    for i in range(1, 5):
        assert m.pick_index(i, vals) == vals[i - 1]
        n += 1
    node = m.SYIndexSwitch()
    assert node.run(2, "a", "b", "c", "d") == ("b", 2)
    assert node.run(4, input4="x") == ("x", 4)
    n += 2
    for i in range(1, 5):
        assert node.check_lazy_status(i) == ["input%d" % i]
        n += 1
    assert _raises(m.pick_index, 0, vals)
    assert _raises(m.pick_index, 5, vals)
    assert _raises(m.pick_index, "1", vals)
    assert _raises(m.pick_index, 3, ["a", "b", None, "d"])
    assert _raises(node.run, 2, "a", None, "c", "d")
    assert _raises(node.check_lazy_status, 9)
    n += 6
    # a falsy but real value (0, empty string) must still pass
    assert m.pick_index(1, [0, 1]) == 0
    assert m.pick_index(1, [""]) == ""
    n += 2
    it = m.SYIndexSwitch.INPUT_TYPES()
    assert it["required"]["select"][1]["max"] == 4
    assert sorted(it["optional"]) == ["input1", "input2", "input3", "input4"]
    assert all(v[1].get("lazy") for v in it["optional"].values())
    assert not (m.ANY != "IMAGE")
    assert m.SYIndexSwitch.RETURN_NAMES == ("selected_value", "selected_index")
    n += 5
    assert m.NODE_CLASS_MAPPINGS["SYIndexSwitch"] is m.SYIndexSwitch
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYIndexSwitch"] == "IndexSwitch SY"
    n += 2
    return n
