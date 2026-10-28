import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_save_with_caption as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.caption_list("a cat", 3) == ["a cat"] * 3; n += 1
    assert m.caption_list("x", 1) == ["x"]; n += 1
    assert raises(m.caption_list, "   ", 1); n += 1
    assert raises(m.caption_list, "x", 0); n += 1
    assert m.SYSaveWithCaption.OUTPUT_NODE is True; n += 1
    return n
