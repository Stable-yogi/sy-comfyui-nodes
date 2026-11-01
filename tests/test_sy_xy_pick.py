import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_xy_pick as m


def run():
    n = 0
    xs, ys = "a\nb\nc", "p\nq"
    assert m.pick(xs, ys, 0) == ("a", "p", 0, 0, 6); n += 1
    assert m.pick(xs, ys, 2) == ("c", "p", 2, 0, 6); n += 1
    assert m.pick(xs, ys, 3) == ("a", "q", 0, 1, 6); n += 1
    assert m.pick(xs, ys, 5) == ("c", "q", 2, 1, 6); n += 1
    assert m.pick(xs, ys, 6, True) == ("a", "p", 0, 0, 6); n += 1
    assert m.pick(xs, "", 1) == ("b", "", 1, 0, 3); n += 1
    assert m.pick("", ys, 1) == ("", "q", 0, 1, 2); n += 1
    assert m.pick("", "", 0) == ("", "", 0, 0, 1); n += 1
    # every index visits a unique cell
    seen = {m.pick(xs, ys, i)[2:4] for i in range(6)}
    assert len(seen) == 6; n += 1
    for args in ((xs, ys, 6), (xs, ys, -1)):
        try:
            m.pick(*args)
            raise SystemExit("must raise")
        except ValueError:
            pass
    n += 2
    assert m.SYXYPick.RETURN_TYPES[:5] == ("STRING", "STRING", "INT", "INT", "INT") and len(m.SYXYPick.RETURN_TYPES) == 7; n += 1
    assert m.SYXYPick.RETURN_NAMES[5:] == ("label", "is_last"); n += 1
    assert m.pick_ex(xs, ys, 4) == ("b", "q", 1, 1, 6, "cell 5 of 6: X=b, Y=q", False); n += 1
    assert m.pick_ex(xs, ys, 5)[6] is True and m.pick_ex(xs, ys, 0)[6] is False; n += 1
    assert m.pick_ex(xs, "", 1)[5] == "cell 2 of 3: X=b"; n += 1
    assert m.pick_ex("", "", 0)[5] == "cell 1 of 1" and m.pick_ex("", "", 0)[6] is True; n += 1
    assert m.pick_ex(xs, ys, 99, False, True)[:5] == ("c", "q", 2, 1, 6); n += 1
    assert m.pick_ex(xs, ys, 6, True, True)[:2] == ("a", "p"); n += 1
    try:
        m.pick_ex(xs, ys, 6)
        raise SystemExit("must raise")
    except ValueError:
        pass
    n += 1
    assert set(m.SYXYPick.INPUT_TYPES()["optional"]) == {"clamp_to_last"}; n += 1
    return n
