import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mute_bypass_switch as m


def run():
    n = 0
    assert [m.mode_number(True, "mute"), m.mode_number(True, "bypass"), m.mode_number(False, "mute"), m.mode_number(False, "bypass")] == [0, 0, 2, 4]
    assert m.mode_number(False, " Bypass ") == 4 and m.mode_number(False, "nonsense") == 2 and m.mode_number(False, None) == 2
    n += 2
    assert m.parse_ids('[3, "7", 3, -1, 2.5, true, null, "x", " 9 "]') == [3, 7, 9]
    assert m.parse_ids("not json") == [] and m.parse_ids('{"a":1}') == [] and m.parse_ids(None) == [] and m.parse_ids([1, 2]) == [1, 2] and m.parse_ids("") == []
    n += 2
    assert m.add_ids("[1]", [2, 1, 5], 5) == [1, 2] and m.add_ids("bad", [4]) == [4] and m.add_ids("[1]", []) == [1] and m.add_ids("[1]", None) == [1]
    n += 1
    sw = [{"id": 1, "pair": "Look", "on": True}, {"id": 2, "pair": " look ", "on": True}, {"id": 3, "pair": "other", "on": True},
          {"id": 4, "pair": "", "on": True}, {"id": 5, "pair": "LOOK", "on": False}]
    assert m.plan_pair(sw, 1) == [2] and m.plan_pair(sw, 5) == [] and m.plan_pair(sw, 3) == [] and m.plan_pair(sw, 4) == []
    assert m.plan_pair(sw, 99) == [] and m.plan_pair([], 1) == [] and m.plan_pair(None, 1) == []
    n += 2
    cls = m.SYMuteBypassSwitch
    req = cls.INPUT_TYPES()["required"]
    assert cls.RETURN_TYPES == () and cls().run() == () and cls.OUTPUT_NODE is False and cls.DESCRIPTION
    assert "tooltip" in req["on"][1] and "tooltip" in req["off_mode"][1] and "tooltip" in cls.INPUT_TYPES()["optional"]["pair"][1]
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYMuteBypassSwitch"] == "MuteBypassSwitch SY"
    n += 3
    return n
