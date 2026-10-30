import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_prompt_builder as m


def run():
    n = 0
    p, notes = m.build_prompt("film", "a town", "she walks", "Hello\nBye", "Japanese", 2, "0-4s: she turns round\n4-8s: she waves")
    assert p == ("Style: film\n\nWorld: a town\n\nAction: she walks\n\nTimeline:\n0-4s: she turns round\n4-8s: she waves\n\n"
                 "<d>[Japanese] Hello</d>\n<d>[Japanese] Bye</d>"); n += 1
    assert notes == ""; n += 1
    p, notes = m.build_prompt("", "", "run", "", "", 0, "")
    assert p == "Action: run" and notes == ""; n += 1
    p, _ = m.build_prompt("", "", "", "Hi there", "", 0, "")
    assert p == "<d>Hi there</d>"; n += 1
    p, _ = m.build_prompt("", "", "", "Hi", "French", 0, "")
    assert p == "<d>[French] Hi</d>"; n += 1
    p, notes = m.build_prompt("", "", "Picture 3 jumps, picture 1 waits", "", "", 2, "")
    assert notes == "action mentions Picture 3 but picture_count is 2", notes; n += 1
    p, notes = m.build_prompt("", "", "x", "", "", 4, "0-4s: ok\nbad line\n5-6: fine")
    assert notes == "time code line 2 is not like 0-4s: text", notes; n += 1
    p, notes = m.build_prompt("  film  ", "  town ", "  go  ", "  hey  ", "  Thai ", 0, "  0-2s:  move  ")
    assert p.startswith("Style: film\n\nWorld: town\n\nAction: go") and "<d>[Thai] hey</d>" in p and "0-2s:  move" in p; n += 1
    p, notes = m.build_prompt("", "", "a" * 4001, "", "", 0, "")
    assert "4000" in notes; n += 1
    for args in (("", "  ", "", "", "", 0, ""), (None, None, None, "\n \n", "", 0, "")):
        try:
            m.build_prompt(*args)
            raise SystemExit("empty must raise")
        except ValueError as e:
            assert "at least one" in str(e)
        n += 1
    assert m.SYH3PromptBuilder.RETURN_TYPES == ("STRING", "STRING"); n += 1
    return n
