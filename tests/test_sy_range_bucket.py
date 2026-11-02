import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_range_bucket as m

LOW, UP = m.INCLUSIVE


def run():
    n = 0
    e = [48.0, 120.0]
    b = m.bucket_index
    assert b(0, e, LOW) == 0 and b(47.99, e, LOW) == 0; n += 1
    assert b(48, e, LOW) == 1 and b(119, e, LOW) == 1; n += 1
    assert b(120, e, LOW) == 2 and b(1e15, e, LOW) == 2; n += 1
    assert b(48, e, UP) == 0 and b(120, e, UP) == 1 and b(120.1, e, UP) == 2; n += 1
    assert b(-1e15, e, LOW) == 0; n += 1
    assert b(5, [], LOW) == 0; n += 1   # no edges: one range
    assert m.parse_edges("48, 120") == e; n += 1
    assert m.parse_edges("") == []; n += 1
    assert m.parse_edges("1,\n2 ,3") == [1.0, 2.0, 3.0]; n += 1
    assert m.parse_labels("a\nb\nc\n\n", 2) == ["a", "b", "c"]; n += 1
    assert m.parse_labels(" a \n b ", 1) == ["a", "b"]; n += 1
    for call, word in ((lambda: m.parse_edges("1, x"), "cannot read"), (lambda: m.parse_edges("5, 3"), "each bigger"),
                       (lambda: m.parse_edges("3, 3"), "each bigger"), (lambda: m.parse_edges("nan"), "ordinary"),
                       (lambda: m.parse_labels("a\nb", 2), "3 lines"), (lambda: m.parse_labels("a\nb\nc\nd", 2), "has 4"),
                       (lambda: b(float("nan"), e, LOW), "ordinary number"), (lambda: b(1, e, "x"), "inclusive must be"),
                       (lambda: b(1, [5.0, 2.0], LOW), "must go up")):
        try:
            call()
            raise SystemExit("bad input must raise")
        except ValueError as ex:
            assert word in str(ex), str(ex)
            n += 1
    node = m.SYRangeBucket()
    assert node.run(60, "48, 120", "short\nmedium\nlong") == ("medium", 1); n += 1
    assert node.run(48, "48, 120", "short\nmedium\nlong", UP) == ("short", 0); n += 1
    return n
