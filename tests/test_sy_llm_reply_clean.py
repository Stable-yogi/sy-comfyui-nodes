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
    eq(m.SYLLMReplyClean.RETURN_TYPES, ("STRING", "STRING"))
    eq(m.reply_clean("<think>hmm\nlet me see</think>\na red fox", strip_thinking=True), "a red fox")
    eq(m.reply_clean("<think>hmm</think>a red fox"), "<think>hmm</think>a red fox")
    eq(m.reply_clean("<THINKING>x</THINKING> y <think>z</think> w", strip_thinking=True), "y  w")
    eq(m.reply_clean("hidden thoughts</think>\nthe answer", strip_thinking=True), "the answer")
    eq(m.reply_clean("a red fox\n\nLet me know if you want changes!", strip_closing_note=True), "a red fox")
    eq(m.reply_clean("a red fox\nHope this helps.\n", strip_closing_note=True), "a red fox")
    eq(m.reply_clean("Let me know", strip_closing_note=True), "Let me know")
    eq(m.reply_clean("a red fox\nLet me know"), "a red fox\nLet me know")
    eq(m.reply_clean_steps("```\n\"hi\"\n```", True, True, True, False, True)[1], ["code fences", "quotes"])
    eq(m.reply_clean_steps("plain")[1], [])
    eq(m.reply_clean_steps("<think>x</think>Sure, here it is:\nfox", strip_thinking=True), ("fox", ["thinking", "intro line"]))
    eq(m.clean_info("abcdef", "abc", ["quotes"]), "Cleaned 6 to 3 characters (removed: quotes).")
    eq(m.clean_info("abc", "abc", []), "Nothing to clean: the text was already tidy (3 characters).")
    eq(m.SYLLMReplyClean().run('"x"'), ("x", "Cleaned 3 to 1 characters (removed: quotes)."))
    eq(m.SYLLMReplyClean().run("<think>a</think>b")[0], "b")
    eq(m.SYLLMReplyClean().run("<think>a</think>b", strip_thinking=False)[0], "<think>a</think>b")
    eq(m.SYLLMReplyClean.RETURN_NAMES, ("text", "info"))
    return n
