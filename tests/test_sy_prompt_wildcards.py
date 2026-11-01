import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_wildcards as m


def run():
    t = "a {red|green|blue} car"
    assert m.expand_choices(t, 1) == m.expand_choices(t, 1)  # same seed, same result
    seen = {m.expand_choices(t, s) for s in range(60)}
    assert seen == {"a red car", "a green car", "a blue car"}, seen
    assert m.expand_choices("no groups", 5) == "no groups"
    assert m.expand_choices("", 5) == ""
    assert m.expand_choices("{only}", 3) == "only"
    assert m.expand_choices(r"\{red|green\}", 3) == "{red|green}"
    assert m.expand_choices(r"\{x\}", 0) == "{x}"
    assert m.expand_choices("{a|b", 0) == "{a|b"  # unclosed stays literal
    assert m.expand_choices("a } b", 0) == "a } b"
    assert {m.expand_choices("{a|}", s) for s in range(40)} == {"a", ""}
    assert {m.expand_choices(r"{x\|y|z}", s) for s in range(40)} == {"x|y", "z"}
    two = {m.expand_choices("{a|b}{c|d}", s) for s in range(100)}
    assert two == {"ac", "ad", "bc", "bd"}, two
    assert m.expand_choices(t, -5) == m.expand_choices(t, 0)
    assert m.expand_choices(t, 2 ** 70) == m.expand_choices(t, m.MAX_SEED)
    assert m.SYPromptChoice().run(t, 7)[0] == m.expand_choices(t, 7)
    return 15 + _extra()


def _extra():
    n = 0
    assert {m.expand_choices("{ a | b }", s, True) for s in range(40)} == {"a", "b"}; n += 1
    assert {m.expand_choices("{ a | b }", s) for s in range(40)} == {" a ", " b "}; n += 1
    text, picks, unclosed = m.expand_choices_info("{x|y} and {z}", 1)
    assert len(picks) == 2 and picks[1] == "z" and unclosed == 0 and text.endswith(" and z"); n += 1
    assert m.expand_choices_info("a { b", 0)[2] == 1; n += 1
    assert m.expand_choices_info("{a|b", 0)[1] == []; n += 1
    assert "No {a|b} groups" in m.choice_info([], 0, 3); n += 1
    info = m.choice_info(["red", ""], 0, 5)
    assert info == "Seed 5 picked 2 group(s): 'red', (nothing)"; n += 1
    assert "WARNING" in m.choice_info([], 1, 0) and "closing" in m.choice_info([], 1, 0); n += 1
    assert "(3 more)" in m.choice_info(["a"] * 15, 0, 0); n += 1
    out = m.SYPromptChoice().run("{only}", 0, False)
    assert out == ("only", "Seed 0 picked 1 group(s): 'only'"); n += 1
    assert m.SYPromptChoice.RETURN_NAMES == ("text", "info"); n += 1
    return n
