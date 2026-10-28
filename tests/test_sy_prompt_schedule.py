import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_schedule as m

TEXT = "0: a cat\n24: a dog\n48: a bird: flying"


def bad(text):
    try:
        m.parse_schedule(text)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    keys = m.parse_schedule(TEXT)
    assert keys == [(0, "a cat"), (24, "a dog"), (48, "a bird: flying")]; n += 1
    assert m.prompt_at(keys, 0) == ("a cat", 24, 3); n += 1
    assert m.prompt_at(keys, 23) == ("a cat", 24, 3); n += 1
    assert m.prompt_at(keys, 24) == ("a dog", 48, 3); n += 1
    assert m.prompt_at(keys, 500) == ("a bird: flying", -1, 3); n += 1
    assert m.parse_schedule("48: b\n0: a") == [(0, "a"), (48, "b")]; n += 1  # sorted
    assert m.parse_schedule("\n# note\n\n5: x\n") == [(5, "x")]; n += 1
    assert m.prompt_at(m.parse_schedule("10: late"), 3) == ("", 10, 1); n += 1  # before first key
    assert m.parse_schedule("") == []; n += 1
    msg = bad("0: ok\nno colon here")
    assert msg and "line 2" in msg and "no colon here" in msg; n += 1
    assert bad("abc: text") is not None; n += 1
    assert bad("-3: text") is not None; n += 1
    assert bad("4:") is not None; n += 1
    assert bad("4:    ") is not None; n += 1
    assert bad(": text") is not None; n += 1
    msg = bad("1: a\n1: b")
    assert msg and "line 2" in msg; n += 1
    try:
        m.prompt_at(keys, -1)
        raise SystemExit("negative frame must raise")
    except ValueError:
        n += 1
    assert m.SYPromptSchedule().run(TEXT, 30) == ("a dog", 48, 3); n += 1
    return n
