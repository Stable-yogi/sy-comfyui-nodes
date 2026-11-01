import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_sections as m


def run():
    n = 0

    def eq(got, want):
        nonlocal n
        assert got == want, "got %r, wanted %r" % (got, want)
        n += 1

    p = {"subject": "a fox", "lighting": "soft light", "style": "oil painting"}
    eq(m.build_sections(p), ("a fox, soft light, oil painting", 3))
    eq(m.build_sections(p, " | "), ("a fox | soft light | oil painting", 3))
    eq(m.build_sections(p, "\n", "label_colon"), ("Subject: a fox\nLighting: soft light\nStyle: oil painting", 3))
    eq(m.build_sections({"subject": "  ", "extra": None}), ("", 0))
    eq(m.build_sections({}), ("", 0))
    eq(m.build_sections({"extra": " x ", "subject": "y"}), ("y, x", 2))
    eq(m.build_sections({"camera": "35mm"}, None, "label_colon"), ("Camera: 35mm", 1))
    eq(m.SYPromptSections().run(subject="s", camera="c")[:2], ("s, c", 2))
    eq(m.SYPromptSections().run(", ", "label_colon", setting="beach")[:2], ("Setting: beach", 1))
    try:
        m.build_sections(p, ", ", "nope")
        raise SystemExit("bad label_mode must raise")
    except ValueError:
        n += 1
    try:
        m.build_sections({"subject": "x" * (m.MAX_INPUT + 1)})
        raise SystemExit("too long input must raise")
    except ValueError:
        n += 1
    eq(m.SYPromptSections.RETURN_TYPES, ("STRING", "INT", "STRING"))
    return n + _extra()


def _extra():
    n = 0
    p = {"subject": "a fox, red", "style": "Red, oil painting", "extra": "a fox"}
    assert m.build_sections(p) == ("a fox, red, Red, oil painting, a fox", 3); n += 1
    assert m.build_sections(p, ", ", "none", True) == ("a fox, red, oil painting", 2); n += 1
    assert m.build_sections(p, ", ", "label_colon", True)[1] == 3; n += 1
    assert m.build_sections({"subject": "x"}, ", ", "none", True) == ("x", 1); n += 1
    info = m.sections_info({"subject": "a fox", "style": "oil"}, "a fox, oil")
    assert info.startswith("Used 2 of 6 parts (subject, style)") and "empty: setting" in info and "10 characters" in info; n += 1
    assert "empty" in m.sections_info({}, ""); n += 1
    out = m.SYPromptSections().run(subject="a, b", style="b, c", remove_repeats=True)
    assert out[0] == "a, b, c" and out[1] == 2 and out[2].startswith("Used 2"); n += 1
    assert m.SYPromptSections.RETURN_NAMES[-1] == "info"; n += 1
    return n
