import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_enhance_request as m


def run():
    n = 0
    t = m.enhance_request("a fox in the snow")
    assert "Idea: a fox in the snow" in t and "about 70 words" in t and t.endswith("Reply with the prompt only."); n += 1
    assert "about 30 words" in m.enhance_request("x", length="short"); n += 1
    assert "about 150 words" in m.enhance_request("x", length="long"); n += 1
    assert "anime" in m.enhance_request("x", style="anime"); n += 1
    assert "commas" in m.enhance_request("x", output_format="comma phrases"); n += 1
    assert "no people" in m.enhance_request("x", notes=" no people "); n += 1
    assert "notes" not in m.enhance_request("x"); n += 1
    for kw in ({"idea": " "}, {"idea": "x", "length": "huge"}, {"idea": "x", "style": "zzz"},
               {"idea": "x", "output_format": "zzz"}, {"idea": "x", "notes": 4}):
        try:
            m.enhance_request(**kw)
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert "Idea: cat" in m.SYPromptEnhanceRequest().run("cat", "short", "photo", "one paragraph")[0]; n += 1
    return n
