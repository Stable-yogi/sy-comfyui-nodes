import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_bookmark as m


def run():
    n = 0
    bms = [{"id": 7, "key": "2"}, {"id": 3, "key": "2"}, {"id": 5, "key": "1"}]
    assert m.find_bookmark(bms, "1")["id"] == 5; n += 1
    assert m.find_bookmark(bms, "2")["id"] == 3; n += 1  # shared key: the lower id wins
    assert m.find_bookmark(bms, "9") is None and m.find_bookmark([], "1") is None; n += 1
    assert m.find_bookmark([{"id": 10, "key": "4"}, {"id": 9, "key": "4"}], 4)["id"] == 9; n += 1  # numbers, not text order
    assert m.find_bookmark([{"id": "b", "key": "4"}, {"id": 2, "key": "4"}], "4")["id"] == 2; n += 1
    assert m.shared_keys(bms) == ["2"] and m.shared_keys([]) == []; n += 1
    assert m.shared_keys([{"id": 1, "key": "3"}, {"id": 2, "key": "3"}, {"id": 3, "key": "3"}, {"id": 4, "key": "1"}, {"id": 5, "key": "1"}]) == ["1", "3"]; n += 1
    assert m.clamp_zoom(1) == 1.0 and m.clamp_zoom(0.01) == m.MIN_ZOOM and m.clamp_zoom(50) == m.MAX_ZOOM; n += 1
    assert m.clamp_zoom("x") == 1.0 and m.clamp_zoom(None) == 1.0 and m.clamp_zoom(float("nan")) == 1.0; n += 1
    # a node 100x50 at (300, 200), zoom 1, view 1000x600: middle (350, 225) must land at (500, 300)
    off = m.centre_offset([300, 200], [100, 50], 1.0, 1000, 600)
    assert off == [150.0, 75.0] and (350 + off[0]) * 1.0 == 500 and (225 + off[1]) * 1.0 == 300; n += 1
    off2 = m.centre_offset([300, 200], [100, 50], 2.0, 1000, 600)
    assert (350 + off2[0]) * 2.0 == 500 and (225 + off2[1]) * 2.0 == 300; n += 1
    cls = m.SYBookmark
    assert cls.RETURN_TYPES == () and cls().run("1", 1.0) == (); n += 1
    req = cls.INPUT_TYPES()["required"]
    assert set(req) == {"key", "zoom"} and req["key"][1]["default"] == "1" and len(req["key"][0]) == 9; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYBookmark"] == "Bookmark SY" and cls.DESCRIPTION; n += 1
    return n
