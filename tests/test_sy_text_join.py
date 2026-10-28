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
    assert node.run(", ", True, "x", "", "y", "") == ("x, y",)
    assert node.run() == ("",)
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYTextJoin"] == "Text Join SY"
    return 12  # checks
