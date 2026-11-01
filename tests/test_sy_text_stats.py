import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_stats as m


def run():
    assert m.text_stats("") == (0, 0, 0, 0)
    assert m.text_stats("abcd") == (4, 1, 1, 1)
    assert m.text_stats("abcde") == (5, 1, 1, 2)
    assert m.text_stats("hello big world\nline two\n") == (25, 5, 2, 7)
    assert m.text_stats("a\n\nb") == (4, 2, 3, 1)
    assert m.text_stats("  spaced   out  ")[1] == 2
    s = m.summary_text((10, 2, 1, 3))
    assert s == "10 chars, 2 words, 1 lines, about 3 tokens"
    out = m.SYTextStats().run("one two\nthree")
    assert out[:4] == (13, 3, 2, 4) and "13 chars" in out[4] and out[5] is False
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYTextStats"] == "Text Stats SY"
    return 9 + _extra()


def _extra():
    n = 0
    assert m.limit_info(10, 0) == (False, "No token limit set"); n += 1
    assert m.limit_info(10, 77) == (False, "Within the limit: 10 of 77 tokens (67 left)"); n += 1
    assert m.limit_info(77, 77)[0] is False; n += 1
    assert m.limit_info(90, 77) == (True, "OVER the limit by 13 tokens (90 of 77): shorten the text"); n += 1
    out = m.SYTextStats().run("a" * 400, 77)
    assert out[3] == 100 and out[5] is True and out[6].endswith("shorten the text") and out[6].startswith("400 chars"); n += 1
    out = m.SYTextStats().run("hi")
    assert out[5] is False and out[6].endswith("No token limit set"); n += 1
    assert len(m.SYTextStats.RETURN_TYPES) == len(m.SYTextStats.RETURN_NAMES) == 7; n += 1
    return n
