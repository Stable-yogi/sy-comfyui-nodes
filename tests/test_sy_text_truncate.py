import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_truncate as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.truncate_text("hello", 5, "...", True) == ("hello", False); n += 1
    assert m.truncate_text("", 1, "...", True) == ("", False); n += 1
    assert m.truncate_text("hello world foo", 10, "...", False) == ("hello w...", True); n += 1
    assert m.truncate_text("hello world foo", 10, "...", True) == ("hello...", True); n += 1
    assert m.truncate_text("hello, world foo", 12, "...", True) == ("hello...", True); n += 1
    assert m.truncate_text("hello world foo", 17, "...", True) == ("hello world foo", False); n += 1
    assert m.truncate_text("hello world foo", 14, "...", True) == ("hello world...", True); n += 1
    assert m.truncate_text("abcdefghij", 6, "...", True) == ("abc...", True); n += 1  # no space: hard cut
    assert m.truncate_text("abcdefghij", 6, "", False) == ("abcdef", True); n += 1
    assert m.truncate_text("abcdefghij", 3, "...", False) == ("...", True); n += 1
    r, t = m.truncate_text("word; more; stuff here", 12, "~", True)
    assert r == "word; more~" and t and len(r) <= 12; n += 1
    for mx in range(3, 20):
        r, _ = m.truncate_text("the quick brown fox jumps over", mx, "...", True)
        assert len(r) <= mx; n += 1
    msg = raises(m.truncate_text, "abcdefghij", 2, "...", True)
    assert msg and "suffix" in msg; n += 1
    msg = raises(m.truncate_text, "abc", 0, "...", True)
    assert msg and "max_chars" in msg; n += 1
    assert raises(m.truncate_text, "abc", 100001, "...", True); n += 1
    assert m.truncate_text("abc", 5, "......", True) == ("abc", False); n += 1  # long suffix is fine if nothing is cut
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYTextTruncate"] == "Text Truncate SY"; n += 1
    assert m.SYTextTruncate.CATEGORY == "SY/Text"; n += 1
    return n
