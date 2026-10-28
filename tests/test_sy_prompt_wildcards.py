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
    assert m.SYPromptChoice().run(t, 7) == (m.expand_choices(t, 7),)
    return 15  # checks
