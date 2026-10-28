import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_if_else_text as m


def run():
    assert m.if_else_text(True, "yes text", "no text") == "yes text"
    assert m.if_else_text(False, "yes text", "no text") == "no text"
    assert m.if_else_text(False, "a", "") == ""
    assert m.SYIfElseText().run(True, "x", "y") == ("x",)
    for bad in ((1, "a", "b"), (True, 5, "b"), (True, "a", None)):
        try:
            m.if_else_text(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYIfElseText.RETURN_TYPES == ("STRING",)
    return 8
