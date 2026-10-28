import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_show_text as m


def run():
    n = 0
    assert m.to_display("abc") == "abc"; n += 1
    assert m.to_display(5) == "5"; n += 1
    assert m.to_display(1.5) == "1.5"; n += 1
    assert m.to_display(True) == "True"; n += 1
    assert m.to_display(None) == ""; n += 1
    assert m.to_display(["a", 2]) == "a\n2"; n += 1
    assert '"k": 1' in m.to_display({"k": 1}); n += 1
    out = m.SYShowText().run("hello")
    assert out["ui"] == {"text": ["hello"]}; n += 1
    assert out["result"] == ("hello",); n += 1
    assert m.SYShowText.OUTPUT_NODE is True; n += 1
    assert m.SYShowText().run(3)["result"] == ("3",); n += 1
    return n
