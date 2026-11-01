import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_few_shot_block as m


def run():
    n = 0

    def eq(got, want):
        nonlocal n
        assert got == want, "got %r, wanted %r" % (got, want)
        n += 1

    eq(m.few_shot_block("Make it short.", [("long one", "short")], "new text"),
       "Make it short.\n\nInput: long one\nOutput: short\n\nInput: new text\nOutput:")
    eq(m.few_shot_block("T", [("a", "b"), ("", "x"), ("c", ""), ("d", "e")], "n", "Q", "A"),
       "T\n\nQ: a\nA: b\n\nQ: d\nA: e\n\nQ: n\nA:")
    eq(m.few_shot_block("", [], "just this"), "Input: just this\nOutput:")
    eq(m.few_shot_block("T", [(None, None)], "n", "", ""), "T\n\nInput: n\nOutput:")
    eq(m.few_shot_block("  T  ", [], "  n  "), "T\n\nInput: n\nOutput:")
    node = m.SYFewShotBlock()
    eq(node.run("T", "n", example_in_2="i", example_out_2="o")[0], "T\n\nInput: i\nOutput: o\n\nInput: n\nOutput:")
    eq(node.run("T", "n", "In", "Out", example_in_1="x", example_out_1="y", example_in_4="p", example_out_4="q")[0],
       "T\n\nIn: x\nOut: y\n\nIn: p\nOut: q\n\nIn: n\nOut:")
    opt = m.SYFewShotBlock.INPUT_TYPES()["optional"]
    eq(len(opt), 8)
    try:
        m.few_shot_block("T", [], "  ")
        raise SystemExit("empty new_input must raise")
    except ValueError:
        n += 1
    try:
        m.few_shot_block("x" * (m.MAX_INPUT + 1), [], "n")
        raise SystemExit("too long input must raise")
    except ValueError:
        n += 1
    eq(m.SYFewShotBlock.RETURN_TYPES, ("STRING", "STRING"))
    eq(m.few_shot_info([("a", "b"), ("c", "d")], "x" * 40), "2 examples used, about 10 tokens.")
    eq(m.few_shot_info([("a", "b")], ""), "1 example used, about 0 tokens.")
    eq(m.few_shot_info([("a", ""), ("", "z"), (None, None)], "abcd"),
       "0 examples used, about 1 tokens. No examples: the model gets only the task (zero-shot). WARNING: example 1 skipped: its answer is empty; example 2 skipped: its input is empty.")
    eq(node.run("T", "n", example_in_1="x")[1].endswith("WARNING: example 1 skipped: its answer is empty."), True)
    eq(node.run("T", "n", example_in_1="x", example_out_1="y")[1].split(",")[0], "1 example used")
    eq(m.SYFewShotBlock.RETURN_NAMES, ("text", "info"))
    return n
