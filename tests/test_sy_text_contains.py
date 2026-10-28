import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_contains as m


def run():
    n = 0
    assert m.text_contains("A Red Cat", "red cat") is True; n += 1
    assert m.text_contains("A Red Cat", "red cat", True) is False; n += 1
    assert m.text_contains("A Red Cat", "Red", True) is True; n += 1
    assert m.text_contains("abc", "xyz") is False; n += 1
    for bad in (("abc", ""), ("abc", 3), (4, "a")):
        try:
            m.text_contains(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert m.SYTextContains().run("Hello", "ell") == (True, "Hello"); n += 1
    assert m.SYTextContains.RETURN_TYPES == ("BOOLEAN", "STRING"); n += 1
    return n
