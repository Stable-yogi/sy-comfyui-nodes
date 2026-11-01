import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_cycle_pick as m


def run():
    text = "red\n\ngreen\n  \nblue\n"
    assert m.parse_items(text) == ["red", "green", "blue"]
    assert m.cycle_pick(text, 0) == ("red", 0, 3)
    assert m.cycle_pick(text, 2) == ("blue", 2, 3)
    assert m.cycle_pick(text, 3) == ("red", 0, 3)
    assert m.cycle_pick(text, 7) == ("green", 1, 3)
    assert m.cycle_pick(text, -1) == ("blue", 2, 3)
    assert m.cycle_pick("only", 99) == ("only", 0, 1)
    assert m.cycle_pick("a\r\nb", 1) == ("b", 1, 2)
    for bad in ("", "   \n\n  "):
        try:
            m.cycle_pick(bad, 0)
            raise SystemExit("empty list must raise")
        except ValueError:
            pass
    # new: modes, comments, info
    abc = "a\nb\nc"
    assert [m.cycle_pick(abc, i, "loop")[0] for i in range(5)] == list("abcab")
    assert [m.cycle_pick(abc, i, "ping-pong")[0] for i in range(8)] == list("abcbabcb")
    assert [m.cycle_pick(abc, i, "stop at last")[0] for i in range(5)] == list("abccc")
    assert m.cycle_pick(abc, -4, "stop at last")[0] == "a"
    assert m.cycle_pick(abc, -1, "ping-pong")[0] == "b"
    assert m.cycle_pick("solo", 5, "ping-pong") == ("solo", 0, 1)
    assert m.cycle_pick("a\nb", 3, "ping-pong")[0] == "b"
    assert m.cycle_pick("a\n#b\nc", 1, "loop", True) == ("c", 1, 2)
    assert m.cycle_pick("a\n#b\nc", 1) == ("#b", 1, 3)             # old behaviour: comments are items
    for bad in (("#x", 0, "loop", True), ("a", 0, "random"), ("a", "x"), ("a", None), ("a", True)):
        try:
            m.cycle_pick(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.pick_info(0, 3, 3, "loop") == "Item 1 of 3, mode loop (counter 3 went round)."
    assert m.pick_info(1, 3, 1) == "Item 2 of 3, mode loop."
    assert "stays on the last" in m.pick_info(2, 3, 9, "stop at last")
    out = m.SYCyclePick().run(abc, 4)
    assert out[:3] == ("b", 1, 3) and out[3].startswith("Item 2 of 3")
    assert m.SYCyclePick.RETURN_TYPES == ("STRING", "INT", "INT", "STRING") and len(m.SYCyclePick.RETURN_NAMES) == 4
    return 36
