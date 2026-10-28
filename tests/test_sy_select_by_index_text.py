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
    assert node.run(1, text_1="x", text_3="z") == ("z", 1)          # gap is skipped
    assert node.run(0, text_8="last") == ("last", 0)
    assert node.run(4, text_2="b", text_1="a", text_10="ignored") == ("a", 0)
    assert len(node.INPUT_TYPES()["optional"]) == 8
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
    assert m.SYSelectByIndexText.RETURN_TYPES == ("STRING", "INT")
    return 19
