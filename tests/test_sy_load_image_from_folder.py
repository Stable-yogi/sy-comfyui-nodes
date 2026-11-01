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
    assert m.SYLoadImageFromFolder.RETURN_TYPES[:3] == ("IMAGE", "MASK", "STRING") and len(m.SYLoadImageFromFolder.RETURN_TYPES) == 6; n += 1
    assert m.SYLoadImageFromFolder.RETURN_NAMES[:3] == ("image", "mask", "filename"); n += 1
    # added value: newest/largest/smallest, index_mode, info
    sized = [("b.png", 30.0, 500), ("A.png", 20.0, 900), ("c.png", 10.0, 100)]
    assert m.order_files(sized, "newest") == ["b.png", "A.png", "c.png"]; n += 1
    assert m.order_files(sized, "largest") == ["A.png", "b.png", "c.png"]; n += 1
    assert m.order_files(sized, "smallest") == ["c.png", "b.png", "A.png"]; n += 1
    assert m.order_files(sized, "name") == ["A.png", "b.png", "c.png"]; n += 1
    assert raises(m.order_files, entries, "largest"); n += 1  # two-value entries have no size
    assert m.order_files(entries, "newest") == ["b.png", "A.png", "c.png"]; n += 1
    assert m.order_files([("a.png", 1.0, 5), ("B.png", 1.0, 5)], "largest") == ["a.png", "B.png"]; n += 1
    name, used, count, info = m.pick_file(sized, 1, "name")
    assert (name, used, count) == ("b.png", 1, 3) and "Picture 2 of 3 (index 1, sorted by name): b.png." == info; n += 1
    name, used, count, info = m.pick_file(sized, 4, "name")
    assert (name, used) == ("b.png", 1) and "wrapped to 1" in info; n += 1
    name, used, count, info = m.pick_file(sized, 9, "name", "clamp")
    assert (name, used) == ("c.png", 2) and "limited to 2" in info; n += 1
    assert m.pick_file(sized, 2, "name", "error")[0] == "c.png"; n += 1
    assert raises(m.pick_file, sized, 3, "name", "error"); n += 1
    assert raises(m.pick_file, sized, 0, "name", "sideways"); n += 1
    assert raises(m.pick_file, [], 0, "name"); n += 1
    try:
        m.pick_file(sized, 3, "name", "error")
    except ValueError as e:
        assert "3 files" in str(e) and "use wrap" in str(e)
        n += 1
    spec = m.SYLoadImageFromFolder.INPUT_TYPES()
    assert list(spec["required"]) == ["subfolder", "index", "sort_by"] and list(spec["optional"]) == ["index_mode"]; n += 1
    assert spec["required"]["sort_by"][0][:2] == ["name", "date"]; n += 1
    return n
