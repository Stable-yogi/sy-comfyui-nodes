import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text as m


def run():
    assert m.clean_text("a  \nb ") == "a  \nb "
    assert m.clean_text("a  \nb \t", True) == "a\nb"
    assert m.clean_text("  lead  ", True) == "  lead"
    assert m.clean_text("", True) == ""
    assert m.clean_text(None) == ""
    assert m.clean_text("x\r\ny\r\n", True) == "x\ny\n"
    assert m.clean_text("\n\n", True) == "\n\n"
    assert m.clean_text("uni é ", True) == "uni é"
    node = m.SYText()
    assert node.run("hi  ", False) == ("hi  ",)
    assert node.run("hi  ", True) == ("hi",)
    assert m.NODE_CLASS_MAPPINGS["SYText"] is m.SYText
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYText"] == "Text SY"
    return 12  # checks
