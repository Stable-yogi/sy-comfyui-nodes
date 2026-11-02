import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_tag_remove as m


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

    eq(m.remove_tags("red, blue, green", ["blue"]), ("red, green", ["blue"]))
    eq(m.remove_tags("red,blue ,  green", ["Blue"], "exact tag", True), ("red, green", ["blue"]))
    eq(m.remove_tags("red, Blue, green", ["blue"], "exact tag", False), ("red, Blue, green", []))
    eq(m.remove_tags("a red car, red, (red:1.2)", ["red"]), ("a red car", ["red", "(red:1.2)"]))
    eq(m.remove_tags("a red car, red", ["red"], "tag contains word"), ("", ["a red car", "red"]))
    eq(m.remove_tags("reddish, red hat", ["red"], "tag contains word"), ("reddish", ["red hat"]))
    eq(m.remove_tags("(red:1.2), blue", ["(red:1.2)"]), ("blue", ["(red:1.2)"]))
    eq(m.remove_tags("one, two, three", ["x"]), ("one, two, three", []))
    eq(m.remove_tags("", ["x"]), ("", []))
    eq(m.remove_tags("one, two", []), ("one, two", []))
    eq(m.remove_tags("a,, b, ,c", ["b"]), ("a, c", ["b"]))
    eq(m.split_entries("a, b\nc\r\n\n d "), ["a", "b", "c", "d"])
    eq(m.split_entries(""), [])
    raises(m.remove_tags, "a", ["a"], "nonsense", True)
    node = m.SYTagRemove()
    eq(node.run("red, blue, green", "blue\ngreen"), ("red", "blue, green", 2))
    eq(m.SYTagRemove.RETURN_TYPES, ("STRING", "STRING", "INT"))
    eq(m.NODE_DISPLAY_NAME_MAPPINGS["SYTagRemove"], "Tag Remove SY")
    eq(m.SYTagRemove.CATEGORY, "SY/Text")
    return n[0]
