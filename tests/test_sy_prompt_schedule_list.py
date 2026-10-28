import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_schedule_list as m


def raises(*args):
    try:
        m.expand_schedule(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    e = m.expand_schedule
    text, seg = e("0: a\n3: b", 5)
    assert text.split("\n") == ["a", "a", "a", "b", "b"]; n += 1
    assert seg == 2; n += 1
    text, seg = e("0: a\n10: b", 5)
    assert text.split("\n") == ["a"] * 5 and seg == 1; n += 1  # key past the end is not a segment
    text, seg = e("2: late", 4)
    assert text.split("\n") == ["", "", "late", "late"] and seg == 1; n += 1
    text, seg = e("", 3)
    assert text.split("\n") == ["", "", ""] and seg == 0; n += 1
    text, seg = e("0: only", 1)
    assert text == "only" and seg == 1; n += 1
    text, seg = e("0: a", 2000)
    assert len(text.split("\n")) == 2000; n += 1
    assert raises("0: a", 2001); n += 1
    assert raises("0: a", 0); n += 1
    assert raises("0: a", -4); n += 1
    assert raises("0: a\nbroken", 5); n += 1
    assert raises("0: a\n0: b", 5); n += 1
    assert m.SYPromptScheduleList().run("0: a\n1: b", 2) == ("a\nb", 2); n += 1
    assert m.SYPromptScheduleList.RETURN_TYPES == ("STRING", "INT"); n += 1
    assert m.MAX_FRAMES == 2000; n += 1
    return n
