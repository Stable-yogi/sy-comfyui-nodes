import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_tag_sort as m


def run():
    n = 0

    def eq(got, want):
        nonlocal n
        assert got == want, "got %r, wanted %r" % (got, want)
        n += 1

    t = "pear, Apple, fig, apple, banana"
    eq(m.tag_sort(t), ["pear", "Apple", "fig", "banana"])
    eq(m.tag_sort(t, dedupe=False), ["pear", "Apple", "fig", "apple", "banana"])
    eq(m.tag_sort(t, order="alphabetical"), ["Apple", "banana", "fig", "pear"])
    eq(m.tag_sort(t, order="shortest_first"), ["fig", "pear", "Apple", "banana"])
    eq(m.tag_sort(t, order="longest_first"), ["banana", "Apple", "pear", "fig"])
    a = m.tag_sort(t, order="shuffle_seeded", seed=5)
    eq(a, m.tag_sort(t, order="shuffle_seeded", seed=5))
    eq(sorted(a), sorted(["pear", "Apple", "fig", "banana"]))
    want = ["pear", "Apple", "fig", "banana"]
    random.Random(5).shuffle(want)
    eq(a, want)
    eq(m.tag_sort("a|b", separator="|", order="alphabetical"), ["a", "b"])
    eq(m.tag_sort(""), [])
    eq(m.tag_sort(None), [])
    eq(m.SYTagSort().run("b, a", ",", "alphabetical", 0, True), ("a, b",))
    for bad in (dict(separator=""), dict(order="nope")):
        try:
            m.tag_sort("a, b", **bad)
            raise SystemExit("bad option must raise")
        except ValueError:
            n += 1
    try:
        m.tag_sort("x" * (m.MAX_INPUT + 1))
        raise SystemExit("too long input must raise")
    except ValueError:
        n += 1
    eq(m.SYTagSort.RETURN_TYPES, ("STRING",))
    return n
