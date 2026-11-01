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
    assert node.run("hi  ", False)[0] == "hi  "
    assert node.run("hi  ", True)[0] == "hi"
    assert m.NODE_CLASS_MAPPINGS["SYText"] is m.SYText
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYText"] == "Text SY"
    return 12 + _extra()


def _extra():
    n = 0
    assert m.clean_text("a\u200bb\ufeff", False, True) == "ab"; n += 1
    assert m.clean_text("a\u00a0b", False, True) == "a b"; n += 1
    assert m.clean_text("a\u200bb") == "a\u200bb"; n += 1
    assert m.clean_text("\n\n  hi  \n\n", False, False, True) == "hi"; n += 1
    assert m.clean_text("  x  \n y ", True, False, True) == "x\n y"; n += 1
    assert m.count_invisible("a\u200b\u00a0") == 2 and m.count_invisible("abc") == 0; n += 1
    assert m.text_info("hello world", "hello world") == "11 character(s), 1 line(s), about 3 tokens"; n += 1
    assert "WARNING: 1 hidden" in m.text_info("a\u200b", "a\u200b"); n += 1
    assert m.text_info("a\u200bb", "ab").endswith("removed 1 hidden character(s)"); n += 1
    assert m.text_info(None, "") == "0 character(s), 0 line(s), about 0 tokens"; n += 1
    out = m.SYText().run("a\u200b ", True, True, True)
    assert out[0] == "a" and "removed 1 hidden" in out[1]; n += 1
    assert m.SYText.RETURN_NAMES == ("text", "info"); n += 1
    return n
