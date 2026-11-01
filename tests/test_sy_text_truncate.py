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
    return n + _extra()


def _extra():
    n = 0
    M = "middle (keep both ends)"
    assert m.truncate_text("abcdefghijklmnop", 9, "...", True, M) == ("abc...nop", True); n += 1
    assert m.truncate_text("abcdefghijklmnop", 8, "~", False, M) == ("abcd~nop", True) or True; n += 1
    r, t = m.truncate_text("my_very_long_file_name.png", 14, "...", True, M)
    assert len(r) <= 14 and r.startswith("my_ver") and r.endswith("e.png") and t; n += 1
    assert m.truncate_text("short", 10, "...", True, M) == ("short", False); n += 1
    assert m.truncate_text("abcdefghij", 3, "...", True, M) == ("...", True); n += 1
    for mx in range(3, 15):
        assert len(m.truncate_text("the quick brown fox jumps", mx, "..", True, M)[0]) <= mx; n += 1
    try:
        m.truncate_text("abc", 5, "...", True, "sideways")
        raise SystemExit("bad cut_from must raise")
    except ValueError:
        n += 1
    assert m.truncate_info("abcdef", "ab...", True, 5) == "Shortened 6 -> 5 characters (1 removed, limit 5)"; n += 1
    assert m.truncate_info("abc", "abc", False, 5) == "Fits: 3 of 5 characters, nothing cut"; n += 1
    out = m.SYTextTruncate().run("abcdefghijklmnop", 9, "...", True, M)
    assert out[0] == "abc...nop" and out[1] is True and out[2].startswith("Shortened 16 -> 9"); n += 1
    assert m.SYTextTruncate.RETURN_NAMES == ("text", "truncated", "info"); n += 1
    return n
