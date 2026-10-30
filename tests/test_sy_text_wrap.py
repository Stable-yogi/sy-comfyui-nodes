import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_wrap as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    t, c = m.wrap_text("one two three four", 9, True)
    assert t == "one two\nthree\nfour" and c == 3; n += 1
    t, c = m.wrap_text("short", 40, True)
    assert t == "short" and c == 1; n += 1
    t, c = m.wrap_text("", 40, True)
    assert t == "" and c == 0; n += 1
    t, c = m.wrap_text("   \n  ", 40, False)
    assert t == "" and c == 0; n += 1
    t, c = m.wrap_text("aaaa bbbb\n\ncccc dddd", 9, True)
    assert t == "aaaa bbbb\n\ncccc dddd" and c == 3; n += 1
    t, c = m.wrap_text("aaaa bbbb\n\ncccc dddd", 40, False)
    assert t == "aaaa bbbb cccc dddd" and c == 1; n += 1
    t, c = m.wrap_text("aaaa\nbbbb", 40, True)
    assert t == "aaaa bbbb"; n += 1
    t, c = m.wrap_text("abcdefghij", 4, True)
    assert t == "abcd\nefgh\nij" and c == 3; n += 1
    t, c = m.wrap_text("well-known fact", 8, True)
    assert "well-" not in t.split("\n")[0] or t.split("\n")[0] == "well-kno"; n += 1
    t, c = m.wrap_text("aa bb\r\n\r\ncc", 40, True)
    assert t == "aa bb\n\ncc" and c == 3; n += 1
    t, c = m.wrap_text("a\n\n\n\nb", 40, True)
    assert t == "a\n\nb"; n += 1
    t, c = m.wrap_text("\n\nstart", 40, True)
    assert t == "start" and c == 1; n += 1
    assert all(len(line) <= 10 for line in m.wrap_text("the quick brown fox jumps over the lazy dog", 10, True)[0].split("\n")); n += 1
    msg = raises(m.wrap_text, "x", 3, True)
    assert msg and "width" in msg; n += 1
    assert raises(m.wrap_text, "x", 1001, True); n += 1
    assert raises(m.wrap_text, None, 10, True); n += 1
    assert m.SYTextWrap().run("one two", 4, True) == ("one\ntwo", 2); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYTextWrap"] == "Text Wrap SY"; n += 1
    return n
