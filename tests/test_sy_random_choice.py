import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_random_choice as m


def run():
    text = "red\n\n  green  \nblue\n"
    a = m.pick_line(text, 7)
    assert a == m.pick_line(text, 7)
    assert a[0] in ("red", "green", "blue") and 0 <= a[1] < 3
    assert ["red", "green", "blue"][a[1]] == a[0]
    seen = {m.pick_line(text, s)[0] for s in range(60)}
    assert seen == {"red", "green", "blue"}
    assert m.pick_line("only", 123) == ("only", 0)
    for bad in ("", "  \n \n"):
        try:
            m.pick_line(bad, 1)
            raise SystemExit("empty must raise")
        except ValueError:
            pass
    assert m.SYRandomChoice().run("x\ny", 3)[0] in ("x", "y")
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYRandomChoice"] == "Random Choice SY"
    return 9 + _extra()


def _extra():
    n = 0
    t = "a\n# note\nb\nc"
    assert [m.pick_line(t, s, m.PICK_MODES[1])[0] for s in range(5)] == ["a", "# note", "b", "c", "a"]; n += 1
    assert [m.pick_line(t, s, m.PICK_MODES[1], True)[0] for s in range(4)] == ["a", "b", "c", "a"]; n += 1
    assert {m.pick_line(t, s, m.PICK_MODES[0], True)[0] for s in range(60)} == {"a", "b", "c"}; n += 1
    assert m.pick_line(t, 2 ** 40, m.PICK_MODES[1], True)[1] == (2 ** 40) % 3; n += 1
    try:
        m.pick_line("# only", 0, m.PICK_MODES[0], True)
        raise SystemExit("only comments must raise")
    except ValueError as e:
        assert "# are skipped" in str(e); n += 1
    try:
        m.pick_line("a", 0, "weird")
        raise SystemExit("bad mode must raise")
    except ValueError:
        n += 1
    assert m.pick_info("a\nb", 1, m.PICK_MODES[1]) == "Picked line 2 of 2 (seed 1, in order)"; n += 1
    assert "WARNING" in m.pick_info("a", 0); n += 1
    out = m.SYRandomChoice().run("x\ny\nz", 4, m.PICK_MODES[1])
    assert out == ("y", 1, "Picked line 2 of 3 (seed 4, in order)"); n += 1
    assert m.SYRandomChoice.RETURN_NAMES[-1] == "info"; n += 1
    return n
