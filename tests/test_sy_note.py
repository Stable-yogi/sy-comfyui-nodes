import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_note as m


def run():
    assert m.clean_note(None) == ("", "info")
    assert m.clean_note("hi", "tip") == ("hi", "tip")
    assert m.clean_note("hi", "bogus") == ("hi", "info")
    assert m.clean_note(5, "warning") == ("5", "warning")
    assert m.SYNote().run("abc", "step") == ("abc",)
    return 5
