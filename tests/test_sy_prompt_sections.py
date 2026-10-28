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
    eq(m.SYPromptSections().run(subject="s", camera="c"), ("s, c", 2))
    eq(m.SYPromptSections().run(", ", "label_colon", setting="beach"), ("Setting: beach", 1))
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
    eq(m.SYPromptSections.RETURN_TYPES, ("STRING", "INT"))
    return n
