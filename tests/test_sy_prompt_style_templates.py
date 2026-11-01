import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_style_templates as m


def run():
    n = 0
    assert len(m.PRESETS) == 12; n += 1
    assert m.NAMES[0] == "none" and len(m.NAMES) == 13; n += 1
    for name, (pre, suf, neg) in m.PRESETS.items():
        assert pre and suf and neg, name
        n += 1
    pos, neg = m.apply_style("a red fox", "anime")
    assert pos.startswith("anime illustration of, a red fox, "); n += 1
    assert neg == m.PRESETS["anime"][2]; n += 1
    pos, neg = m.apply_style("fox", "photo", "extra bad")
    assert neg.endswith(", extra bad"); n += 1
    assert m.apply_style(" fox ", "none", " bad ") == ("fox", "bad"); n += 1
    pos, _ = m.apply_style("", "pixel art")
    assert pos == "pixel art of, 16-bit, limited palette, crisp pixels"; n += 1
    for bad in (("x", "nope"), (3, "photo")):
        try:
            m.apply_style(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert m.SYPromptStyleTemplates().run("fox", "cinematic")[0].startswith("cinematic still of"); n += 1
    return n + _extra()


def _extra():
    n = 0
    pos, neg = m.apply_style("a fox, Sharp Focus", "photo", "lowres", True)
    assert pos == "photo of, a fox, Sharp Focus, natural light, realistic skin texture, 35mm"; n += 1
    assert neg == "cartoon, painting, illustration, blurry, lowres"; n += 1
    pos, neg = m.apply_style("a fox, sharp focus", "photo", "lowres", False)
    assert pos.count("sharp focus") == 2 and neg.count("lowres") == 2; n += 1
    pos, neg, info = m.apply_style_info("fox", "photo")
    assert (pos, neg) == m.apply_style("fox", "photo") and info.startswith("Style photo: added"); n += 1
    assert "left out 2" in m.apply_style_info("sharp focus, lowres", "photo", "lowres", True)[2]; n += 1
    assert "WARNING" in m.apply_style_info("  ", "anime")[2]; n += 1
    assert "left as it is" in m.apply_style_info("x", "none")[2]; n += 1
    out = m.SYPromptStyleTemplates().run("fox", "anime", "bad", False)
    assert len(out) == 3 and out[0].startswith("anime illustration of") and out[1].endswith(", bad"); n += 1
    assert m.SYPromptStyleTemplates.RETURN_NAMES == ("positive", "negative", "info"); n += 1
    return n
