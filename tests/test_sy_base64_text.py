import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_base64_text as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.base64_text("abc", "encode", False) == "YWJj"; n += 1
    assert m.base64_text("YWJj", "decode", False) == "abc"; n += 1
    assert m.base64_text("", "encode", False) == ""; n += 1
    assert m.base64_text("", "decode", False) == ""; n += 1
    assert m.base64_text("a", "encode", False) == "YQ=="; n += 1
    assert m.base64_text("YQ", "decode", False) == "a"; n += 1  # missing padding
    assert m.base64_text("YWI", "decode", False) == "ab"; n += 1
    for s in ("café naïve", "smile \U0001F600!", "plain", "line\nbreak", "ÿþ"):
        for u in (False, True):
            assert m.base64_text(m.base64_text(s, "encode", u), "decode", u) == s; n += 1
    e = m.base64_text("ûÿ¾?>", "encode", True)
    assert "+" not in e and "/" not in e; n += 1
    assert m.base64_text("YWJj\nZGVm", "decode", False) == "abcdef"; n += 1  # whitespace ignored
    assert m.base64_text("YQ==", "decode", True) == "a"; n += 1
    msg = raises(m.base64_text, "!!!!", "decode", False)
    assert msg and "text is not valid base64" in msg; n += 1
    msg = raises(m.base64_text, "/w==", "decode", False)  # byte 0xff is not UTF-8
    assert msg and "text is not valid base64" in msg; n += 1
    msg = raises(m.base64_text, "A", "decode", False)
    assert msg and "text is not valid base64" in msg; n += 1
    msg = raises(m.base64_text, "abc", "flip", False)
    assert msg and "mode" in msg; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYBase64Text"] == "Base64 Text SY"; n += 1
    assert m.SYBase64Text.CATEGORY == "SY/Text"; n += 1
    return n
