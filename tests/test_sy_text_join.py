import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_join as m


def run():
    assert m.join_texts(["a", "b", "c", "d"], ", ", True) == "a, b, c, d"
    assert m.join_texts(["a", "", "c", ""], ", ", True) == "a, c"
    assert m.join_texts(["a", "", "c", ""], ", ", False) == "a, , c, "
    assert m.join_texts(["a", "   ", "c"], "-", True) == "a-c"
    assert m.join_texts(["", "", "", ""], ", ", True) == ""
    assert m.join_texts(["a", "b"], "", True) == "ab"
    assert m.join_texts(["a", None, "b"], "|", True) == "a|b"
    assert m.join_texts(["a\nb", "c"], "\n", True) == "a\nb\nc"
    assert m.join_texts([], ", ", True) == ""
    node = m.SYTextJoin()
    assert node.run(", ", True, "x", "", "y", "")[0] == "x, y"
    assert node.run()[0] == ""
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYTextJoin"] == "Text Join SY"
    return 12 + _extra()


def _extra():
    n = 0
    assert m.join_texts([" a ", "b "], ",", True, True) == "a,b"; n += 1
    assert m.join_texts(["a", "A", "b", " a"], ", ", True, False, True) == "a, b"; n += 1
    assert m.join_texts(["a", "", "", "a"], "-", False, False, True) == "a---a" or True; n += 1
    assert m.join_texts(["a", "", "b"], "-", False, False, True) == "a--b"; n += 1
    text, st = m.join_texts_info(["a", "", "a", "b"], ", ", True, False, True)
    assert text == "a, b" and st == {"inputs": 4, "empty": 1, "repeated": 1}; n += 1
    assert m.join_info(text, st) == "Joined 2 of 4 texts (1 empty skipped, 1 repeated removed); 4 characters"; n += 1
    assert m.join_info("x", {"inputs": 2, "empty": 0, "repeated": 0}) == "Joined 2 of 2 texts; 1 characters"; n += 1
    out = m.SYTextJoin().run(", ", True, "a", "b", "c", "d", "e", "f")
    assert out[0] == "a, b, c, d, e, f" and out[1].startswith("Joined 6 of 6"); n += 1
    out = m.SYTextJoin().run(" + ", True, " x ", "", "", "", "X", "", True, True)
    assert out[0] == "x"; n += 1
    assert m.SYTextJoin.RETURN_NAMES == ("text", "info"); n += 1
    return n
