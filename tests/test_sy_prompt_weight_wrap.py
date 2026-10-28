import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_weight_wrap as m


def raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def run():
    n = 0
    S = m.STYLES
    assert m.wrap_prompt("cat", S[0], 1.2) == "(cat:1.2)"; n += 1
    assert m.wrap_prompt("cat", S[0], 0.85) == "(cat:0.85)"; n += 1
    assert m.wrap_prompt("cat", S[0], 2) == "(cat:2)"; n += 1
    assert m.wrap_prompt("cat", S[0], 1.0) == "cat"; n += 1
    assert m.wrap_prompt("  cat, dog ", S[1]) == "(cat, dog)"; n += 1
    assert m.wrap_prompt("cat", S[2]) == "((cat))"; n += 1
    assert m.wrap_prompt("cat", S[3]) == "[cat]"; n += 1
    assert m.wrap_prompt("cat", S[4]) == "{cat}"; n += 1
    assert m.wrap_prompt("   ", S[1]) == ""; n += 1
    assert raises(lambda: m.wrap_prompt("cat", "bogus")); n += 1
    assert raises(lambda: m.wrap_prompt("cat", S[0], 11)); n += 1
    assert raises(lambda: m.wrap_prompt("cat", S[0], -1)); n += 1
    assert raises(lambda: m.wrap_prompt(3)); n += 1
    assert m.SYPromptWeightWrap().run("x", S[0], 1.5) == ("(x:1.5)",); n += 1
    return n
