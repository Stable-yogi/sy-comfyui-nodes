import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_stacking_keeper as m


def run():
    n = 0
    # ---- reading a saved stacking
    assert m.parse_order("[3, 1, 2]") == ["3", "1", "2"]; n += 1
    assert m.parse_order("[]") == [] and m.parse_order("") == [] and m.parse_order(None) == []; n += 1
    assert m.parse_order("{bad") == [] and m.parse_order('{"a": 1}') == [] and m.parse_order("7") == []; n += 1
    assert m.parse_order('[1, "2", 3.5, true, null, [4], 5, "", "  "]') == ["1", "2", "5"]; n += 1
    assert m.parse_order("[1, 2, 1, \"2\", 3]") == ["1", "2", "3"]; n += 1
    assert m.parse_order([4, "x"]) == ["4", "x"]; n += 1
    assert len(m.parse_order(json.dumps(list(range(1, 30001))))) == m.MAX_IDS; n += 1
    # ---- merging with the nodes that exist now
    assert m.merge_order(["3", "1", "2"], [1, 2, 3]) == ["3", "1", "2"]; n += 1
    assert m.merge_order(["3", "1", "2"], ["1", "3"]) == ["3", "1"]; n += 1  # node 2 was deleted; ids may be numbers or text
    assert m.merge_order(["3", "1"], [1, 2, 3, 7]) == ["3", "1", "2", "7"]; n += 1  # new nodes go on top, in number order
    assert m.merge_order([], [5, 2, 9, 10]) == ["2", "5", "9", "10"]; n += 1  # 10 after 9: sorted as numbers
    assert m.merge_order([], ["b", 2, "a"]) == ["2", "a", "b"]; n += 1
    assert m.merge_order(["1", "2"], []) == []; n += 1
    # ---- raise and lower
    assert m.raise_to_front(["1", "2", "3"], 1) == ["2", "3", "1"]; n += 1
    assert m.raise_to_front(["1", "2", "3"], "3") == ["1", "2", "3"]; n += 1
    assert m.raise_to_front(["1", "2"], 9) == ["1", "2", "9"]; n += 1
    assert m.send_to_back(["1", "2", "3"], 3) == ["3", "1", "2"]; n += 1
    assert m.send_to_back(["1", "2", "3"], "1") == ["1", "2", "3"]; n += 1
    assert m.send_to_back(["1", "2"], 9) == ["9", "1", "2"]; n += 1
    # ---- a round trip through the saved text
    order = m.raise_to_front(m.send_to_back(["1", "2", "3", "4"], 4), 2)
    assert m.merge_order(m.parse_order(json.dumps(order)), [1, 2, 3, 4]) == order == ["4", "1", "3", "2"]; n += 1
    # ---- shape of the node
    cls = m.SYStackingKeeper
    assert cls.RETURN_TYPES == () and cls().run("[1]", True) == (); n += 1
    req = cls.INPUT_TYPES()["required"]
    assert set(req) == {"order", "restore_on_open"} and req["order"][1]["default"] == "[]" and req["restore_on_open"][1]["default"] is True; n += 1
    assert "SYStackingKeeper" in m.NODE_CLASS_MAPPINGS and m.NODE_DISPLAY_NAME_MAPPINGS["SYStackingKeeper"] == "Stacking Keeper SY"; n += 1
    assert cls.CATEGORY.endswith("/Utility"); n += 1
    return n
