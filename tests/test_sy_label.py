import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_label as m


def run():
    n = 0
    assert m.clean_label("Hi", 36, "gold", "left") == ("Hi", 36, "gold", "left"); n += 1
    assert m.clean_label(None)[0] == ""; n += 1
    assert m.clean_label("x", 5)[1] == m.MIN_SIZE and m.clean_label("x", 999)[1] == m.MAX_SIZE; n += 1
    assert m.clean_label("x", "abc")[1] == 36 and m.clean_label("x", None)[1] == 36; n += 1
    assert m.clean_label("x", 40, "pink", "middle")[2:] == ("gold", "left"); n += 1
    assert m.clean_label("x" * 5000)[0] == "x" * m.MAX_TEXT; n += 1
    assert m.clean_label("x", 40, "purple", "centre")[2:] == ("purple", "centre"); n += 1
    assert m.label_lines("\n\nOne\nTwo\n\n") == ["One", "Two"]; n += 1
    assert m.label_lines("") == [] and m.label_lines(None) == [] and m.label_lines("  \n ") == []; n += 1
    assert m.label_lines("a\r\nb") == ["a", "b"]; n += 1
    assert m.label_lines("a\n\nb") == ["a", "", "b"]; n += 1
    cls = m.SYLabel
    assert cls.RETURN_TYPES == () and cls().run("x", 20, "gold", "left") == (); n += 1
    req = cls.INPUT_TYPES()["required"]
    assert set(req) == {"text", "size", "colour", "align"} and req["size"][1]["default"] == 36; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYLabel"] == "Label SY"; n += 1
    assert cls.CATEGORY == "SY/Notes" and cls.DESCRIPTION; n += 1
    return n
