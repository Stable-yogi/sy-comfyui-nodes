import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_if_else_text as m


def run():
    assert m.if_else_text(True, "yes text", "no text") == "yes text"
    assert m.if_else_text(False, "yes text", "no text") == "no text"
    assert m.if_else_text(False, "a", "") == ""
    assert m.SYIfElseText().run(True, "x", "y")[0] == "x"
    for bad in ((1, "a", "b"), (True, 5, "b"), (True, "a", None)):
        try:
            m.if_else_text(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    # new: fallback when the chosen text is empty, and info
    assert m.if_else_text(True, "", "other", True) == "other"
    assert m.if_else_text(False, "a", "   ", True) == "a"
    assert m.if_else_text(True, "", "other") == ""                    # off by default: old behaviour
    assert m.if_else_text(True, "", "", True) == ""                   # both empty stays empty
    assert m.if_else_text(True, "keep", "other", True) == "keep"
    assert m.if_else_text_info(True, "abc", "x") == "Condition is yes: took if_true (3 characters)."
    assert m.if_else_text_info(False, "abc", "") == "Condition is no: took if_false (0 characters)."
    assert m.if_else_text_info(True, "", "other", True) == "Took if_false because if_true was empty (5 characters)."
    assert m.if_else_text_info(False, "mine", " ", True) == "Took if_true because if_false was empty (4 characters)."
    assert m.SYIfElseText().run(False, "a", "", True) == ("a", "Took if_true because if_false was empty (1 character).")
    assert m.SYIfElseText.RETURN_TYPES == ("STRING", "STRING") and m.SYIfElseText.RETURN_NAMES[0] == "text"
    return 19
