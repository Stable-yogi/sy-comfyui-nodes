import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_llm_reply_clean as m


def run():
    n = 0

    def eq(got, want):
        nonlocal n
        assert got == want, "got %r, wanted %r" % (got, want)
        n += 1

    eq(m.reply_clean("Here is your prompt:\n\na red fox"), "a red fox")
    eq(m.reply_clean("Sure! Here you go:\na red fox"), "a red fox")
    eq(m.reply_clean("A fox: it runs\nfast"), "A fox: it runs\nfast")
    eq(m.reply_clean("Here is the prompt:\na red fox", strip_preamble=False), "Here is the prompt:\na red fox")
    eq(m.reply_clean("```text\na red fox\n```"), "a red fox")
    eq(m.reply_clean("```\na\n```", strip_code_fences=False), "```\na\n```")
    eq(m.reply_clean('"a red fox"'), "a red fox")
    eq(m.reply_clean('"a" and "b"'), '"a" and "b"')
    eq(m.reply_clean('"a red fox"', strip_wrapping_quotes=False), '"a red fox"')
    eq(m.reply_clean("one\n\ntwo", first_paragraph_only=True), "one")
    eq(m.reply_clean("one\n\ntwo"), "one\n\ntwo")
    eq(m.reply_clean("one\n\n\n\n\ntwo"), "one\n\ntwo")
    eq(m.reply_clean("one\n\n\n\ntwo", collapse_blank_lines=False), "one\n\n\n\ntwo")
    eq(m.reply_clean("Okay, here it is:\n```\n\"hello\"\n```\n\nbye", first_paragraph_only=True), "hello")
    eq(m.reply_clean(""), "")
    eq(m.reply_clean(None), "")
    try:
        m.reply_clean("x" * (m.MAX_INPUT + 1))
        raise SystemExit("too long input must raise")
    except ValueError:
        n += 1
    eq(m.SYLLMReplyClean.RETURN_TYPES, ("STRING",))
    return n
