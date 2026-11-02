import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_latch_value as m


def run():
    n = 0
    s = m.latch_step
    assert s(None, "a") == ("a", "a", False); n += 1            # first value is taken
    assert s("a", "b") == ("a", "a", True); n += 1              # later value ignored
    assert s("a", "b", True, True) == ("b", "b", False); n += 1  # reset takes the new one
    assert s("a", "b", False) == ("b", None, False); n += 1     # latch off: pass through, clear
    assert s(None, "", True) == ("", "", False); n += 1         # an empty text can be latched
    assert s("", "x") == ("", "", True); n += 1
    try:
        s(None, 5)
        raise SystemExit("non text must raise")
    except ValueError as e:
        assert "must be text" in str(e)
        n += 1
    m._STORE.clear()
    node = m.SYLatchValue()
    assert node.run("a", True, False, "7") == ("a", False); n += 1
    assert node.run("b", True, False, "7") == ("a", True); n += 1
    assert node.run("z", True, False, "8") == ("z", False); n += 1   # other node id keeps its own store
    assert node.run("c", True, True, "7") == ("c", False); n += 1
    assert node.run("d", True, False, "7") == ("c", True); n += 1
    assert node.run("e", False, False, "7") == ("e", False); n += 1  # off clears the store
    assert "7" not in m._STORE; n += 1
    assert node.run("f", True, False, "7") == ("f", False); n += 1
    assert m.SYLatchValue.IS_CHANGED() != m.SYLatchValue.IS_CHANGED(); n += 1   # NaN never equals itself
    m._STORE.clear()
    return n
