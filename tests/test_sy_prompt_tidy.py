import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_tidy as m


def _fails(**kw):
    try:
        m.tidy_prompt(**kw)
    except ValueError:
        return True
    return False


def run():
    n = 0
    t = m.tidy_prompt
    # defaults: clean only
    assert t("a ,, b ,  c,")[0] == "a, b, c"; n += 1
    assert t("a, b")[2] == "No changes, 3 tokens (about)"; n += 1
    assert t("")[:2] == ("", 0); n += 1
    # join and separators
    assert t("a", "b")[0] == "a, b"; n += 1
    assert t("a,", "b")[0] == "a, b"; n += 1
    assert t("a", "b", "new line")[0] == "a\nb"; n += 1
    assert t("a", "b", "space")[0] == "a b"; n += 1
    assert t("a.", "b", "period")[0] == "a. b"; n += 1
    assert t("a", "  ")[0] == "a"; n += 1
    assert t("", "b")[0] == "b"; n += 1
    assert "oined" in t("a", "b")[2]; n += 1
    # clean off
    assert t("a ,, b", clean=False)[0] == "a ,, b"; n += 1
    # duplicates
    out, _, info = t("cat, Dog, cat, DOG, bird", remove_duplicates=True)
    assert out == "cat, Dog, bird" and "emoved 2 duplicates" in info; n += 1
    assert t("cat, (cat:1.4), (cat:1.2)", remove_duplicates=True)[0] == "(cat:1.4)"; n += 1
    assert t("(cat:1.2), cat, dog", remove_duplicates=True)[0] == "(cat:1.2), dog"; n += 1
    assert t("a, a", remove_duplicates=False)[0] == "a, a"; n += 1
    assert t("a, b, a", remove_duplicates=True)[0] == "a, b"; n += 1
    # weights
    out, _, info = t("(cat:1.2), (dog:0.5), bird", weights="strip all")
    assert out == "cat, dog, bird" and "tripped 2 weights" in info; n += 1
    assert t("((cat)), [dog]", weights="strip all")[0] == "cat, dog"; n += 1
    assert t("(cat:1.234), (dog:1.0)", weights="normalise to 1 decimal")[0] == "(cat:1.2), (dog:1.0)"; n += 1
    assert "ounded 1 weight" in t("(cat:1.234), (dog:1.0)", weights="normalise to 1 decimal")[2]; n += 1
    assert t("(cat:1.234)", weights="keep")[0] == "(cat:1.234)"; n += 1
    assert t("(cat:1.5), <lora:x:0.85>", weights="normalise to 1 decimal")[0] == "(cat:1.5), <lora:x:0.85>"; n += 1
    # lowercase
    assert t("Cat, DOG")[0] == "Cat, DOG"; n += 1
    assert t("Cat, <lora:MyLora:0.8>, DOG", lowercase=True)[0] == "cat, <lora:MyLora:0.8>, dog"; n += 1
    # trigger and remove words
    assert t("a, b, c", trigger_words="c, z")[0] == "c, z, a, b"; n += 1
    assert t("a, (z:1.1), b", trigger_words="Z")[0] == "Z, a, b"; n += 1
    assert t("a, b", trigger_words="x, X")[0] == "x, a, b"; n += 1
    assert "rigger word" in t("a", trigger_words="x")[2]; n += 1
    assert t("a, b, c, d", remove_words="B, d")[0] == "a, c"; n += 1
    assert t("a, (b:1.2), c", remove_words="b")[0] == "a, c"; n += 1
    assert "emoved 2 listed tags" in t("a, b, c, d", remove_words="b, d")[2]; n += 1
    assert t("a, b", remove_words="nothing")[0] == "a, b"; n += 1
    # token counting and cut
    assert m.estimate_tokens("one two three four five six seven eight nine ten") == 13; n += 1
    assert m.estimate_tokens("abcdefgh", "characters/4 estimate") == 2; n += 1
    assert t("a b, c d", token_style="characters/4 estimate")[1] == 2; n += 1
    out, cnt, info = t("one two, three four, five six, seven eight", max_tokens=6)
    assert out == "one two, three four" and cnt == 6 and info.endswith("cut 2 tags at the end"); n += 1
    assert t("one two, three four", max_tokens=100)[0] == "one two, three four"; n += 1
    out, cnt, info = t("alpha beta gamma delta epsilon", max_tokens=2)
    assert out == "alpha beta gamma delta epsilon" and "WARNING" in info; n += 1
    assert t("t1, a b c d, e f g h", trigger_words="t1", max_tokens=1)[0] == "t1"; n += 1
    # order of operations
    assert t("cat, (cat:1.4), dog", remove_duplicates=True, weights="strip all")[0] == "cat, dog"; n += 1
    assert t("Cat, x", extra_text="cat, y", remove_duplicates=True, lowercase=True)[0] == "cat, x, y"; n += 1
    out, cnt, info = t("A, a, (b:1.234), c", "", "comma", True, True, "strip all", True, "", "", 0)
    assert out == "a, b, c" and info == "Lowercased, removed 1 duplicate, stripped 1 weight, 4 tokens (about)", info; n += 1
    info = t("a, a, a, (b:1.2), (c:1.2), d, e, f", remove_duplicates=True, weights="strip all", max_tokens=5)[2]
    assert info == "Removed 2 duplicates, stripped 2 weights, 4 tokens (about), cut 3 tags at the end", info; n += 1
    # refusals
    assert _fails(text=5); n += 1
    assert _fails(text="a", separator="slash"); n += 1
    assert _fails(text="a", weights="maybe"); n += 1
    assert _fails(text="a", token_style="exact"); n += 1
    assert _fails(text="a", max_tokens=-1); n += 1
    assert _fails(text="a", max_tokens=4097); n += 1
    assert _fails(text="a", max_tokens=1.5); n += 1
    assert _fails(text="a", trigger_words="x", remove_words="X"); n += 1
    assert _fails(text="a" * 2000001); n += 1
    assert _fails(text="a", extra_text=3); n += 1
    # node class and pass-through
    node = m.SYPromptTidy()
    assert node.run("a ,, b")[0] == "a, b"; n += 1
    off = node.run("A ,, b ,", "zzz", remove_duplicates=True, enabled=False)
    assert off[0] == "A ,, b ," and off[1] == 6 and off[2].startswith("Off:"), off; n += 1
    assert m.SYPromptTidy.RETURN_NAMES == ("text", "token_estimate", "info"); n += 1
    assert m.SYPromptTidy.RETURN_TYPES == ("STRING", "INT", "STRING"); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYPromptTidy"] == "Prompt Tidy SY"; n += 1
    assert list(node.INPUT_TYPES()["required"]) == ["text"]; n += 1
    return n
