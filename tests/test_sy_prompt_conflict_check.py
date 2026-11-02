import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_conflict_check as m


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

    eq(len(m.BUILTIN_PAIRS) >= 20, True)
    eq(m.find_conflicts("a night photo in the day"), [("day", "night")])
    eq(m.find_conflicts("daylight and night"), [])
    eq(m.find_conflicts("A NIGHT scene, DAY"), [("day", "night")])
    eq(m.find_conflicts("indoor, outdoor"), [("indoor", "outdoor")])
    eq(m.find_conflicts("a black and white photo, colour grading"), [("black and white", "colour")])
    eq(m.find_conflicts("close-up of a face, wide shot"), [("close-up", "wide shot")])
    eq(m.find_conflicts("a red car"), [])
    eq(m.find_conflicts(""), [])
    eq(m.find_conflicts("cat and dog", [("cat", "dog")]), [("cat", "dog")])
    eq(m.find_conflicts("sunday night", []), [])
    eq(m.parse_pairs("a | b\n\n c|d "), [("a", "b"), ("c", "d")])
    eq(m.parse_pairs(""), [])
    raises(m.parse_pairs, "just one")
    raises(m.parse_pairs, "a | b | c")
    raises(m.parse_pairs, "a | ")
    eq(m.format_report([]), "No conflicts found")
    eq(m.format_report([("day", "night")]), "day <-> night")
    node = m.SYPromptConflictCheck()
    eq(node.run("day and night"), ("day and night", "day <-> night", 1))
    eq(node.run("hello", "")[1:], ("No conflicts found", 0))
    eq(node.run("cat dog", "cat | dog")[2], 1)
    raises(node.run, "x", "bad line")
    eq(m.NODE_DISPLAY_NAME_MAPPINGS["SYPromptConflictCheck"], "Prompt Conflict Check SY")
    return n[0]
