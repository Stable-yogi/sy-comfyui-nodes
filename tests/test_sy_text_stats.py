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
    assert out[:4] == (13, 3, 2, 4) and "13 chars" in out[4]
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYTextStats"] == "Text Stats SY"
    return 9
