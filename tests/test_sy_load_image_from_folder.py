import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_load_image_from_folder as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    entries = [("b.png", 30.0), ("A.png", 20.0), ("c.png", 10.0)]
    assert m.order_files(entries, "name") == ["A.png", "b.png", "c.png"]; n += 1
    assert m.order_files(entries, "date") == ["c.png", "A.png", "b.png"]; n += 1
    assert m.choose_file(entries, 0, "name") == "A.png"; n += 1
    assert m.choose_file(entries, 2, "name") == "c.png"; n += 1
    assert m.choose_file(entries, 3, "name") == "A.png"; n += 1
    assert m.choose_file(entries, 10, "date") == "A.png"; n += 1
    assert raises(m.choose_file, [], 0, "name"); n += 1
    assert raises(m.choose_file, entries, 0, "size"); n += 1
    assert m.order_files([("x.png", 1.0), ("a.png", 1.0)], "date") == ["a.png", "x.png"]; n += 1
    assert m.SYLoadImageFromFolder.RETURN_TYPES == ("IMAGE", "MASK", "STRING"); n += 1
    return n
