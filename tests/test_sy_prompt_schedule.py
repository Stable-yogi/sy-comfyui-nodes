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


def _fails(fn, args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


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
    assert m.SYPromptSchedule().run(TEXT, 30) == ("a dog", 48, 3, "a bird: flying", 0.25, "Frame 30: using the key at frame 24; next key at frame 48 (25% of the way)."); n += 1
    r = m.schedule_run
    assert r(keys, 0) == ("a cat", 24, 3, "a dog", 0.0, "Frame 0: using the key at frame 0; next key at frame 24 (0% of the way)."); n += 1
    assert r(keys, 12)[3:5] == ("a dog", 0.5); n += 1
    assert r(keys, 500) == ("a bird: flying", -1, 3, "", 0.0, "Frame 500: using the key at frame 48; no later key."); n += 1
    assert r(keys, 60, 48) == ("a cat", 24, 3, "a dog", 0.5, "Frame 12 (looped from 60): using the key at frame 0; next key at frame 24 (50% of the way)."); n += 1
    assert r(keys, 10, 48)[5].startswith("Frame 10: "); n += 1
    late = m.parse_schedule("10: late\n20: later")
    assert r(late, 3) == ("", 10, 2, "late", 0.0, "Frame 3: before the first key at frame 10, so the prompt is empty; next key at frame 10 (0% of the way)."); n += 1
    assert r(late, 3, 0, "use first prompt")[0] == "late"; n += 1
    assert r(late, 3, 0, "use first prompt")[5].startswith("Frame 3: before the first key at frame 10, so the first prompt is used"); n += 1
    assert r([], 5) == ("", -1, 0, "", 0.0, "The schedule has no keys, so the prompt is empty."); n += 1
    assert r(keys, 1, 0, "empty")[0] == "a cat"; n += 1
    assert _fails(r, (keys, 5, -1)); n += 1
    assert _fails(r, (keys, 5, 0, "sideways")); n += 1
    assert _fails(r, (keys, -1)); n += 1
    assert m.SYPromptSchedule().run(TEXT, 60, 48)[0] == "a cat"; n += 1
    assert m.SYPromptSchedule().run("", 3)[5] == "The schedule has no keys, so the prompt is empty."; n += 1
    assert m.SYPromptSchedule.RETURN_NAMES == ("prompt", "next_key_frame", "key_count", "next_prompt", "blend", "info"); n += 1
    return n
