import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_emphasis_strip as m


def run():
    n = 0

    def eq(got, want):
        nonlocal n
        assert got == want, "got %r, wanted %r" % (got, want)
        n += 1

    s = m.strip_emphasis
    eq(s("a (red:1.2) fox"), "a red fox")
    eq(s("a ((red)) fox"), "a red fox")
    eq(s("a [red] fox"), "a red fox")
    eq(s("a (red:.5), (blue:-0.3) fox"), "a red, blue fox")
    eq(s("(a (b:1.1) c:1.3)"), "a b c")
    eq(s("a \\(red\\) fox"), "a (red) fox")
    eq(s("a \\(red:1.2\\) fox"), "a (red:1.2) fox")
    eq(s("fox <lora:style:0.8>, red"), "fox <lora:style:0.8>, red")
    eq(s("fox <lora:style:0.8>, red", remove_lora_tags=True), "fox, red")
    eq(s("red BREAK blue"), "red BREAK blue")
    eq(s("red BREAK blue", remove_break=True), "red blue")
    eq(s("red, BREAK, blue", remove_break=True), "red, blue")
    eq(s("BREAKFAST (BREAK:1.1)", remove_break=True), "BREAKFAST")
    eq(s("a  ,  b ,, c"), "a, b, c")
    eq(s(",a,"), "a")
    eq(s("(a:1.1)\n(b:1.2)"), "a\nb")
    eq(s(""), "")
    eq(s(None), "")
    try:
        s("x" * (m.MAX_INPUT + 1))
        raise SystemExit("too long input must raise")
    except ValueError:
        n += 1
    eq(m.SYPromptEmphasisStrip.RETURN_TYPES, ("STRING",))
    return n
