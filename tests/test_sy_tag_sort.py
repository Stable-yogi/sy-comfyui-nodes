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
    eq(m.SYTagSort().run("b, a", ",", "alphabetical", 0, True)[0], "a, b")
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
    eq(m.SYTagSort.RETURN_TYPES, ("STRING", "STRING"))
    return n + _extra()


def _extra():
    n = 0
    t = "dog, ohwx, Cat, dog, watermark, bird"
    assert m.tag_sort(t, trigger_first="ohwx") == ["ohwx", "dog", "Cat", "watermark", "bird"]; n += 1
    assert m.tag_sort(t, order="alphabetical", trigger_first="ohwx", remove_tags="Watermark") == ["ohwx", "bird", "Cat", "dog"]; n += 1
    assert m.tag_sort("a, b", trigger_first="ohwx, woman") == ["ohwx", "woman", "a", "b"]; n += 1
    assert m.tag_sort("a, OHWX, b", trigger_first="ohwx") == ["ohwx", "a", "b"]; n += 1
    assert m.tag_sort("a, b, a", dedupe=False, trigger_first="a") == ["a", "b"]; n += 1
    assert m.tag_sort("a, b", remove_tags="a\nb") == []; n += 1
    assert m.tag_sort("a|b|c", separator="|", remove_tags="b") == ["a", "c"]; n += 1
    tags, st = m.tag_sort_full(t, trigger_first="ohwx, woman", remove_tags="watermark")
    assert st == {"removed": 1, "duplicates": 1, "pinned_moved": 1, "pinned_added": 1, "total": 6}, st; n += 1
    assert tags[:2] == ["ohwx", "woman"]; n += 1
    info = m.sort_info(st, "keep", len(tags))
    assert info == "5 tag(s) out (from 6), order: keep; 1 repeated removed, 1 unwanted removed, 1 moved to the front, 1 was missing and added at the front", info; n += 1
    assert m.sort_info({"removed": 0, "duplicates": 0, "pinned_moved": 0, "pinned_added": 0, "total": 2}, "keep", 2) == "2 tag(s) out (from 2), order: keep"; n += 1
    out = m.SYTagSort().run("b, a, b", ",", "alphabetical", 0, True, "z")
    assert out[0] == "z, a, b" and out[1].startswith("3 tag(s) out (from 3)"); n += 1
    assert m.SYTagSort.RETURN_NAMES == ("text", "info"); n += 1
    return n
