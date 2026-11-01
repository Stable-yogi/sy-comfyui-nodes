import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_enhance_request as m


def _fails(fn, args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


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
    assert "watercolor painting" in m.enhance_request("x", style="watercolor"); n += 1
    assert "pixel art" in m.enhance_request("x", style="pixel art"); n += 1
    assert "bullet list" in m.enhance_request("x", output_format="bullet points"); n += 1
    assert list(m.STYLES)[:7] == ["photo", "cinematic", "anime", "painting", "3d render", "product shot", "any style"]; n += 1
    assert "Do not include: text, big hands" in m.enhance_request("x", avoid="  text,   big hands "); n += 1
    assert "Do not include" not in m.enhance_request("x", avoid="  "); n += 1
    t2 = m.enhance_request("x", also_negative=True)
    assert t2.endswith("lists what to avoid.") and "Reply with the prompt only." not in t2; n += 1
    assert m.enhance_request("x", avoid="a", also_negative=True).split("\n")[-2] == "Do not include: a"; n += 1
    assert m.request_info("a fox in snow") == "Asks for medium any style prompt (about 70 words, one paragraph) from an idea of 4 words."; n += 1
    assert m.request_info("fox", "short", "anime", "comma phrases", "text", True) == "Asks for short anime prompt (about 30 words, comma phrases) from an idea of 1 word. Also asks for an avoid list and a negative line."; n += 1
    assert m.request_info("x " * 400).endswith("WARNING: the idea is long; a short idea works best."); n += 1
    assert _fails(m.enhance_request, ("x", "medium", "any style", "one paragraph", "", 5)); n += 1
    out = m.SYPromptEnhanceRequest().run("cat", "short", "photo", "one paragraph", "", "text", True)
    assert "Do not include: text" in out[0] and out[1].endswith("Also asks for an avoid list and a negative line."); n += 1
    assert m.SYPromptEnhanceRequest().run("cat", "short", "photo", "one paragraph")[1].startswith("Asks for short photo prompt"); n += 1
    assert m.SYPromptEnhanceRequest.RETURN_NAMES == ("request", "info"); n += 1
    return n
