import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_select_by_index_text as m


def run():
    t = ["a", "b", "c"]
    assert m.select_text(0, t) == ("a", 0)
    assert m.select_text(2, t) == ("c", 2)
    assert m.select_text(3, t) == ("a", 0)       # wraps
    assert m.select_text(7, t) == ("b", 1)
    assert m.select_text(-1, t) == ("c", 2)      # counts from the end
    assert m.select_text(5, ["only"]) == ("only", 0)
    assert m.select_text(9, list("abcdefgh")) == ("b", 1)
    node = m.SYSelectByIndexText()
    assert node.run(1, text_1="x", text_3="z")[:2] == ("z", 1)      # gap is skipped
    assert node.run(0, text_8="last")[:2] == ("last", 0)
    assert node.run(4, text_2="b", text_1="a", text_10="ignored")[:2] == ("a", 0)
    assert len(node.INPUT_TYPES()["optional"]) == 10
    for bad in ((0, []), (1.5, ["a"]), (True, ["a"]), (0, ["a", 5]), (0, list("abcdefghi"))):
        try:
            m.select_text(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    try:
        node.run(0)
        raise SystemExit("no text must raise")
    except ValueError:
        pass
    # new: out_of_range, skip_empty, count, info
    assert m.select_text(5, t, "clamp") == ("c", 2)
    assert m.select_text(-3, t, "clamp") == ("a", 0)
    assert m.select_text(1, t, "error") == ("b", 1)
    for idx in (3, -1):
        try:
            m.select_text(idx, t, "error")
            raise SystemExit("error mode must raise")
        except ValueError as e:
            assert "outside 0 to 2" in str(e) and "3 texts are" in str(e)
    try:
        m.select_text(1, ["x"], "error")
    except ValueError as e:
        assert "only 1 text is connected" in str(e)
    try:
        m.select_text(0, t, "sideways")
        raise SystemExit("must raise")
    except ValueError as e:
        assert "out_of_range" in str(e)
    assert m.select_text(1, ["a", "", "c"], "wrap", True) == ("c", 1)   # empty text left out
    assert m.select_text(1, ["a", "", "c"]) == ("", 1)                  # old behaviour keeps it
    assert m.select_text(0, ["  ", "b"], "wrap", True) == ("b", 0)
    try:
        m.select_text(0, ["", "  "], "wrap", True)
        raise SystemExit("all empty must raise")
    except ValueError as e:
        assert "empty" in str(e)
    assert m.select_info(1, 1, 3) == "Sent text 2 of 3."
    assert "went round" in m.select_info(4, 1, 3)
    assert node.run(4, text_1="a", text_2="b") == ("a", 0, 2, "Sent text 1 of 2 (index 4 went round or was clamped).")
    assert node.run(1, "wrap", True, text_1="a", text_2="", text_3="c")[:3] == ("c", 1, 2)
    try:
        node.run(0, "wrap", True, text_1="", text_2="  ")
        raise SystemExit("all empty must raise")
    except ValueError:
        pass
    assert m.SYSelectByIndexText.RETURN_TYPES == ("STRING", "INT", "INT", "STRING") and len(m.SYSelectByIndexText.RETURN_NAMES) == 4
    assert set(m.SYSelectByIndexText.INPUT_TYPES()["required"]) == {"index"} and {"out_of_range", "skip_empty"} <= set(m.SYSelectByIndexText.INPUT_TYPES()["optional"])
    return 42
