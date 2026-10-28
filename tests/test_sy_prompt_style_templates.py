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
    return n
