import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_control_panel as m


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def rows_json(*rows):
    return json.dumps(list(rows))


def run():
    n = 0
    # ---- parse: good input and defaults
    assert m.parse_rows("") == [] and m.parse_rows(None) == [] and m.parse_rows("[]") == []; n += 1
    r = m.parse_rows('[{"name": " Steps ", "kind": "int", "value": 20, "min": 1, "max": 150, "step": 1}]')[0]
    assert r["name"] == "Steps" and r["kind"] == "int" and r["value"] == 20 and r["min"] == 1 and r["max"] == 150; n += 1
    r = m.parse_rows("[{}]")[0]
    assert r["kind"] == "float" and r["value"] == 0 and r["min"] is None and r["max"] is None and r["options"] == [] and r["mode"] == "fixed"; n += 1
    assert m.parse_rows('[{"kind": "switch"}]')[0]["value"] is False; n += 1
    assert m.parse_rows('[{"kind": "text"}]')[0]["value"] == ""; n += 1
    assert m.parse_rows('[{"kind": "text", "value": null, "name": null}]')[0]["name"] == ""; n += 1
    assert len(m.parse_rows(json.dumps([{}] * 32))) == 32; n += 1
    r = m.parse_rows('[{"kind": "float", "value": 5000000, "min": 0, "max": 10}]')[0]
    assert r["value"] == 5000000; n += 1  # a value outside the range is allowed: the range is only the slider range
    assert m.parse_rows(m.rows_to_json(m.parse_rows('[{"name": "a", "kind": "dropdown", "options": ["x", "y"], "value": "y"}]'))) == \
        m.parse_rows('[{"name": "a", "kind": "dropdown", "options": ["x", "y"], "value": "y"}]'); n += 1
    # ---- parse: refusals
    assert "not readable" in refuses(m.parse_rows, "{bad"); n += 1
    assert "must be a list" in refuses(m.parse_rows, '{"a": 1}'); n += 1
    msg = refuses(m.parse_rows, json.dumps([{}] * 33))
    assert msg and "33" in msg and "32" in msg; n += 1
    assert "Row 2 is not" in refuses(m.parse_rows, "[{}, 7]"); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"kind": "slider"}]'); n += 1
    assert "Row 2" in refuses(m.parse_rows, '[{}, {"name": 5}]'); n += 1
    assert "lowest value" in refuses(m.parse_rows, '[{"min": 5, "max": 1}]'); n += 1
    assert "step" in refuses(m.parse_rows, '[{"step": 0}]'); n += 1
    assert "step" in refuses(m.parse_rows, '[{"step": -1}]'); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"value": "5"}]'); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"value": true}]'); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"value": NaN}]'); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"value": Infinity}]'); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"max": "9"}]'); n += 1
    assert "true or false" in refuses(m.parse_rows, '[{"kind": "switch", "value": 1}]'); n += 1
    assert "text" in refuses(m.parse_rows, '[{"kind": "text", "value": 3}]'); n += 1
    assert "list of text" in refuses(m.parse_rows, '[{"kind": "dropdown", "options": [1, 2]}]'); n += 1
    assert "list of text" in refuses(m.parse_rows, '[{"kind": "dropdown", "options": "a"}]'); n += 1
    assert "seed mode" in refuses(m.parse_rows, '[{"kind": "seed", "mode": "spin"}]'); n += 1
    # ---- outputs by kind
    rows = m.parse_rows(rows_json(
        {"name": "Cfg", "kind": "float", "value": 7.5},
        {"name": "Steps", "kind": "int", "value": 24.4},
        {"name": "On", "kind": "switch", "value": True},
        {"name": "Prompt", "kind": "text", "value": "a red apple"},
        {"name": "Model", "kind": "dropdown", "options": ["a.safetensors", "b.safetensors"], "value": "b.safetensors"},
        {"name": "Seed", "kind": "seed", "value": 1234567890123},
    ))
    out, seeds = m.build_outputs(rows, "1")
    assert len(out) == m.MAX_ROWS and out[6:] == (None,) * (m.MAX_ROWS - 6); n += 1
    assert out[0] == 7.5 and isinstance(out[0], float); n += 1
    assert out[1] == 24 and isinstance(out[1], int) and not isinstance(out[1], bool); n += 1
    assert out[2] is True and out[3] == "a red apple" and out[4] == "b.safetensors"; n += 1
    assert out[5] == 1234567890123 and seeds == {5: 1234567890123}; n += 1
    # ---- no clamping: the value goes out as typed, far outside the slider range
    big = m.parse_rows(rows_json({"kind": "float", "value": 123456.5, "min": 0, "max": 10}, {"kind": "int", "value": -500, "min": 0, "max": 10}))
    o, _ = m.build_outputs(big)
    assert o[0] == 123456.5 and o[1] == -500; n += 1
    # ---- int rounding
    assert m.row_output(m.parse_rows('[{"kind": "int", "value": 2.5}]')[0], 1) == 2 and m.row_output(m.parse_rows('[{"kind": "int", "value": 2.6}]')[0], 1) == 3; n += 1
    # ---- dropdown refusal and an empty list
    bad = m.parse_rows(rows_json({"name": "Model", "kind": "dropdown", "options": ["a", "b"], "value": "c"}))
    msg = refuses(m.build_outputs, bad)
    assert msg and "Row 1" in msg and "Model" in msg and "'c'" in msg; n += 1
    assert m.build_outputs(m.parse_rows(rows_json({"kind": "dropdown", "options": [], "value": "free"})))[0][0] == "free"; n += 1
    # ---- seed modes
    fx = m.parse_rows(rows_json({"kind": "seed", "value": 42, "mode": "fixed"}))
    assert m.build_outputs(fx, "a")[0][0] == 42 and m.build_outputs(fx, "a")[0][0] == 42; n += 1
    rd = m.parse_rows(rows_json({"kind": "seed", "value": 42, "mode": "random"}))
    seen = {m.build_outputs(rd, "b")[0][0] for _ in range(8)}
    assert len(seen) > 1 and all(0 <= s <= m.MAX_SEED for s in seen); n += 1
    inc = m.parse_rows(rows_json({"kind": "seed", "value": 10, "mode": "increment"}))
    assert [m.build_outputs(inc, "c")[0][0] for _ in range(3)] == [10, 11, 12]; n += 1
    inc2 = m.parse_rows(rows_json({"kind": "seed", "value": 500, "mode": "increment"}))
    assert m.build_outputs(inc2, "c")[0][0] == 500; n += 1  # the typed number changed: start again from it
    assert [m.build_outputs(inc, "d")[0][0] for _ in range(2)] == [10, 11]; n += 1  # another node counts on its own
    top = m.parse_rows(rows_json({"kind": "seed", "value": m.MAX_SEED, "mode": "increment"}))
    assert [m.build_outputs(top, "e")[0][0] for _ in range(2)] == [m.MAX_SEED, 0]; n += 1
    assert m.build_outputs(m.parse_rows(rows_json({"kind": "seed", "value": -5})))[0][0] == 0; n += 1
    # ---- names and labels
    assert m.row_label({"name": ""}, 3) == "Row 3" and m.row_label({"name": "Cfg"}, 3) == "Cfg"; n += 1
    # ---- run through the class, like ComfyUI does it
    cls = m.SYControlPanel
    res = cls().run(rows_json({"kind": "seed", "value": 7, "mode": "random"}, {"kind": "int", "value": 9}), "node1")
    assert isinstance(res, dict) and len(res["result"]) == m.MAX_ROWS and res["result"][1] == 9; n += 1
    assert json.loads(res["ui"]["sy_seeds"][0]) == {"0": res["result"][0]} or json.loads(res["ui"]["sy_seeds"][0]).get("0") == res["result"][0]; n += 1
    assert cls().run(rows_json({"kind": "int", "value": 9}))["ui"] == {}; n += 1
    assert cls().run("[]")["result"] == (None,) * m.MAX_ROWS; n += 1
    # ---- caching: random and counting seeds run every time, the rest only when the rows change
    nan = cls.IS_CHANGED(rows_json({"kind": "seed", "mode": "random"}))
    assert nan != nan; n += 1
    nan = cls.IS_CHANGED(rows_json({"kind": "seed", "mode": "increment"}))
    assert nan != nan; n += 1
    same = rows_json({"kind": "seed", "mode": "fixed"}, {"kind": "float", "value": 1})
    assert cls.IS_CHANGED(same) == same; n += 1
    bad_in = cls.IS_CHANGED("{bad")
    assert bad_in != bad_in; n += 1
    # ---- shape of the node
    assert len(cls.RETURN_TYPES) == m.MAX_ROWS == len(cls.RETURN_NAMES); n += 1
    assert all(t == "*" for t in cls.RETURN_TYPES) and cls.RETURN_NAMES[0] == "out1" and cls.RETURN_NAMES[-1] == "out32"; n += 1
    assert set(m.OUT_TYPES) == set(m.KINDS); n += 1
    assert "SYControlPanel" in m.NODE_CLASS_MAPPINGS and m.NODE_DISPLAY_NAME_MAPPINGS["SYControlPanel"] == "Control Panel SY"; n += 1
    return n
