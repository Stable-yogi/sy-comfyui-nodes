import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_skin_prompt_guard as m

OPEN = "A photoreal video, deep focus, natural soft light."


def g(prompt, **kw):
    lists = kw.pop("lists", None) or m.default_lists()
    kw.setdefault("opening_text", OPEN)
    return m.guard_prompt(prompt, lists, **kw)


def run():
    n = 0
    # g) empty
    assert g("") == ("", "The prompt is empty.", False)
    assert g("   \n")[0] == ""
    n += 2
    # nothing to change, opening off
    t, r, c = g("A woman walks on a beach.", add_opening_line=False)
    assert (t, r, c) == ("A woman walks on a beach.", "Nothing to change.", False)
    n += 1
    # c) shine words removed, case-insensitive, whole words only
    t, r, c = g("A woman with Glowing, shiny skin and a glossy look.", add_opening_line=False)
    assert "glow" not in t.lower() and "shiny" not in t.lower() and "glossy" not in t.lower(), t
    assert "skin and a look." in t and ",," not in t and "  " not in t and c is True
    assert "glowing" in r.lower() and "3 changes" in r
    t, _, c = g("The shinestone glows", add_opening_line=False)   # not whole words
    assert t == "The shinestone glows" and c is False
    t, _, _ = g("her wet skin and WET   LOOK shine", add_opening_line=False)
    assert "wet" not in t.lower() and "shine" not in t.lower()
    n += 5
    # b) negation clauses
    t, r, _ = g("A woman, no oily skin, walks.", add_opening_line=False)
    assert t == "A woman, walks." and "no oily skin" in r, (t, r)
    t, _, _ = g("A woman without shiny skin and bright eyes", add_opening_line=False)
    assert "shiny" not in t and "without" not in t and t.endswith("and bright eyes"), t
    t, _, _ = g("Avoid glow. She smiles.", add_opening_line=False)
    assert t == ". She smiles." or t == "She smiles." or t.endswith("She smiles."), t
    assert "Avoid" not in t and "avoid" not in t
    t, _, _ = g("She is not hungry and has very oily skin", add_opening_line=False)   # oily is far from 'not' and clause ends at 'and'
    assert t.startswith("She is not hungry") and "oily" not in t, t
    n += 4
    # a) quoted text is never touched
    t, _, _ = g('She says "no oily skin, glowing pores" and looks shiny.', add_opening_line=False)
    assert '"no oily skin, glowing pores"' in t and "shiny" not in t, t
    t, _, _ = g("He whispers “shiny glow” softly, glowing.", add_opening_line=False)
    assert "“shiny glow”" in t and t.endswith("softly") or "“shiny glow” softly" in t, t
    # a negation clause must not swallow a quote
    t, _, _ = g('no shiny "keep glow here"', add_opening_line=False)
    assert '"keep glow here"' in t, t
    n += 3
    # warn mode: text unchanged, words listed
    src = "A woman with glowing skin, no oily skin, freckles, pores, skin texture."
    t, r, c = g(src, mode="warn", add_opening_line=False)
    assert t == src and c is False and "not removed" in r and "glowing" in r and "no oily skin" in r, (t, r)
    assert "not dropped" in r
    n += 2
    # d) skin detail words
    t, r, _ = g("Close up, freckles, pores, skin texture, smiling.", add_opening_line=False)
    assert "freckles" in t and "pores" not in t and "skin texture" not in t and "smiling" in t, t
    assert "kept the first" in r
    t, _, c = g("Close up, freckles, pores, smiling.", add_opening_line=False)   # only two: untouched
    assert t == "Close up, freckles, pores, smiling." and c is False
    t, _, _ = g("Close up, freckles, pores, skin texture, smiling.", add_opening_line=False, keep_skin_words=True)
    assert t == "Close up, freckles, pores, skin texture, smiling."
    t, _, _ = g("visible pores, pores, imperfections", add_opening_line=False)   # longest phrase counts once
    assert t == "visible pores", t
    n += 4
    # e) trigger first, then opening, then the prompt
    t, _, c = g("A woman walks.", trigger_text="ohwx woman")
    assert t == "ohwx woman. " + OPEN + " A woman walks." and c is True, t
    t, _, _ = g("A woman walks.", trigger_text="ohwx woman", add_opening_line=False)
    assert t == "ohwx woman. A woman walks.", t
    t, _, _ = g("A woman walks.")
    assert t == OPEN + " A woman walks."
    t, _, _ = g("A woman walks.", add_opening_line=False, opening_text="")
    assert t == "A woman walks."
    t, _, _ = g("ohwx woman, runs.", trigger_text="ohwx woman", add_opening_line=False)   # already at the start
    assert t == "ohwx woman, runs.", t
    t, r, _ = g("A woman walks.", trigger_text="ohwx woman", add_opening_line=False)
    assert "trigger" in r.lower()
    n += 6
    # f) idempotent
    for src, kw in (("A woman, no oily skin, glowing, freckles, pores, skin texture, says \"shiny\".", {"trigger_text": "ohwx woman"}),
                    ("Plain prompt.", {}), ("Plain prompt.", {"trigger_text": "xyz, abc"}),
                    ("shiny", {"trigger_text": "ohwx woman.", "keep_skin_words": True})):
        once = g(src, **kw)[0]
        twice, rep, changed = g(once, **kw)
        assert twice == once and changed is False and rep == "Nothing to change.", (once, twice, rep)
    n += 4
    # bad mode
    try:
        g("x", mode="loud")
        raise SystemExit("bad mode must raise")
    except ValueError:
        pass
    n += 1
    # list file parsing
    txt = ("# comment\n[shine]\nSparkle\nglow  worm\n\n[negation]\nnope\n[opening]\nmy style = Hello   there.\n")
    lists = m.parse_word_list(txt)
    assert lists["shine"] == ["sparkle", "glow worm"] and lists["negation"] == ["nope"]
    assert lists["opening"] == {"my style": "Hello there."}
    assert lists["skin_detail"] == m.DEFAULT_LISTS["skin_detail"]   # missing section keeps the default
    t, _, _ = g("A sparkle and a glow worm, glowing.", lists=lists, add_opening_line=False)
    assert "sparkle" not in t and "glow worm" not in t and "glowing" in t, t
    for bad in ("word before section\n", "[nope]\n", "[opening]\nno equals sign\n"):
        try:
            m.parse_word_list(bad)
            raise SystemExit("bad list must raise: %r" % bad)
        except ValueError:
            pass
    n += 7
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "words.txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write(txt)
        assert m.load_word_list(p)["shine"] == ["sparkle", "glow worm"]
        assert m.load_word_list(os.path.join(d, "missing.txt")) == m.default_lists()
    n += 2
    # the shipped file matches the built-in lists
    shipped = m.load_word_list()
    assert shipped == m.default_lists(), "assets/sy_skin_words.txt differs from the built-in lists"
    n += 1
    # node class
    node = m.SYH3SkinPromptGuard()
    t, r, c = node.run("A woman, glossy skin.", trigger_text="ohwx")
    assert t.startswith("ohwx. " + OPEN) and "glossy" not in t and c is True
    assert node.run("Hi", opening_style="none")[0] == "Hi"
    try:
        node.run("Hi", opening_style="weird")
        raise SystemExit("bad style must raise")
    except ValueError:
        pass
    n += 3
    return n
