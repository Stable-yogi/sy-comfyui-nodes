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
    assert m.SYPromptWeightWrap().run("x", S[0], 1.5)[0] == "(x:1.5)"; n += 1
    return n + _extra()


def _extra():
    n = 0
    S = m.STYLES
    assert m.split_tags("a, (b, c:1.2), d") == ["a", "(b, c:1.2)", "d"]; n += 1
    assert m.wrap_prompt("cat, dog", S[0], 1.2, True) == "(cat:1.2), (dog:1.2)"; n += 1
    assert m.wrap_prompt("cat, (dog, mouse:1.1)", S[1], 1.2, True) == "(cat), ((dog, mouse:1.1))"; n += 1
    assert m.wrap_prompt("(cat:1.3)", S[0], 1.2) == "((cat:1.3):1.2)"; n += 1
    assert m.wrap_prompt("(cat:1.3)", S[0], 1.5, False, "replace the weight") == "(cat:1.5)"; n += 1
    assert m.wrap_prompt("(cat:1.3)", S[0], 1.5, False, "leave as it is") == "(cat:1.3)"; n += 1
    assert m.wrap_prompt("(cat:1.3), dog", S[0], 0.8, True, "leave as it is") == "(cat:1.3), (dog:0.8)"; n += 1
    assert m.wrap_prompt("(cat:1.3)", S[0], 1.0, False, "replace the weight") == "cat"; n += 1
    assert m.wrap_prompt(" , ", S[0], 1.2, True) == ""; n += 1
    assert raises(lambda: m.wrap_prompt("x", S[0], 1.2, False, "nope")); n += 1
    assert "WARNING" in m.wrap_info("a (b", "x", S[0], 1.2) and "round" in m.wrap_info("a (b", "x", S[0], 1.2); n += 1
    assert "above 1.5" in m.wrap_info("a", "x", S[0], 2); n += 1
    assert m.wrap_info("a, b", "x", S[0], 1.2, True) == "Wrapped 2 tag(s) one by one as (text:1.2)"; n += 1
    assert m.wrap_info("", "", S[1], 1) == "Empty text: nothing to wrap"; n += 1
    out = m.SYPromptWeightWrap().run("a, b", S[3], 1.2, True)
    assert out[0] == "[a], [b]" and out[1].startswith("Wrapped 2 tag(s)"); n += 1
    assert m.SYPromptWeightWrap.RETURN_NAMES == ("text", "info"); n += 1
    return n
