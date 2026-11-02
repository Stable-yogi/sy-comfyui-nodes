import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_variants as m


def run():
    n = [0]

    def eq(got, want):
        n[0] += 1
        assert got == want, "got %r want %r" % (got, want)

    def raises(fn, *a):
        n[0] += 1
        try:
            fn(*a)
        except ValueError:
            return
        raise AssertionError("expected ValueError")

    eq(m.expand("a {red|blue|green} car", 500), ["a red car", "a blue car", "a green car"])
    eq(m.expand("{a|b} {1|2}", 500), ["a 1", "a 2", "b 1", "b 2"])
    eq(m.expand("no choices", 500), ["no choices"])
    eq(m.expand("{a|b|c}", 2), ["a", "b"])
    eq(m.expand("x{a|}y", 10), ["xay", "xy"])
    eq(m.expand("{solo}", 10), ["solo"])
    eq(m.expand("\\{a|b\\}", 10), ["{a|b}"])
    eq(m.expand("keep \\{ brace and {a|b}", 10), ["keep { brace and a", "keep { brace and b"])
    eq(m.total_count("{a|b} {1|2|3}"), 6)
    eq(m.total_count("plain"), 1)
    eq(m.combination("{a|b} {1|2}", 0), "a 1")
    eq(m.combination("{a|b} {1|2}", 3), "b 2")
    eq(m.combination("{a|b} {1|2}", 5), "a 2")  # wraps: 5 % 4 = 1
    eq(m.combination("{a|b} {1|2}", 1), "a 2")
    raises(m.parse_template, "{a|{b|c}}")
    raises(m.parse_template, "{a|b")
    raises(m.parse_template, "a|b}")
    raises(m.expand, "{a|b}", 0)
    node = m.SYPromptVariants()
    eq(node.run("{r|g|b}", 4, 2), ("g", "r\ng", 3))
    eq(node.run("{a|b}{c|d}", 0, 500)[1], "ac\nad\nbc\nbd")
    eq(m.NODE_DISPLAY_NAME_MAPPINGS["SYPromptVariants"], "Prompt Variants SY")
    return n[0]
