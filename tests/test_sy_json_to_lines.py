import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_json_to_lines as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    doc = m.parse_json('{"b": 1, "a": {"x": true, "y": null, "z": [10, "t"]}, "s": "hi"}')
    assert m.json_to_lines(doc) == ["b: 1", "x: true", "y: null", "z[0]: 10", "z[1]: t", "s: hi"]; n += 1
    assert m.json_to_lines(doc, "key = value")[0] == "b = 1"; n += 1
    assert m.json_to_lines(doc, "value only") == ["1", "true", "null", "10", "t", "hi"]; n += 1
    assert m.json_to_lines(doc, "dotted.path: value") == [
        "b: 1", "a.x: true", "a.y: null", "a.z.0: 10", "a.z.1: t", "s: hi"]; n += 1
    assert m.json_to_lines(doc, "dotted.path: value", 4, True)[0] == "a.x: true"; n += 1
    # depth: deeper parts become compact JSON
    assert m.json_to_lines(doc, "key: value", 1) == ['b: 1', 'a: {"x":true,"y":null,"z":[10,"t"]}', "s: hi"]; n += 1
    assert m.json_to_lines(doc, "dotted.path: value", 2)[3] == 'a.z: [10,"t"]'; n += 1
    # edge: scalars, empty containers, top-level list, one item
    assert m.json_to_lines(5) == ["5"]; n += 1
    assert m.json_to_lines("a\nb") == ["a\\nb"]; n += 1
    assert m.json_to_lines({}) == ["{}"]; n += 1
    assert m.json_to_lines({"e": []}) == ["e: []"]; n += 1
    assert m.json_to_lines([1, 2]) == ["[0]: 1", "[1]: 2"]; n += 1
    assert m.json_to_lines([1, 2], "dotted.path: value") == ["0: 1", "1: 2"]; n += 1
    assert m.json_to_lines({"k": 1.5}) == ["k: 1.5"]; n += 1
    # deepest allowed
    deep = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": {"j": {"k": 1}}}}}}}}}}}
    assert m.json_to_lines(deep, "dotted.path: value", 10)[0] == 'a.b.c.d.e.f.g.h.i.j: {"k":1}'; n += 1
    # refusals
    assert "Invalid JSON: line 1" in _raises(m.parse_json, '{"a": }'); n += 1
    assert "empty" in _raises(m.parse_json, "   "); n += 1
    assert "format must be" in _raises(m.json_to_lines, 1, "xml"); n += 1
    assert "max_depth" in _raises(m.json_to_lines, 1, "key: value", 0); n += 1
    node = m.SYJSONToLines()
    assert node.run('{"a": 1}', "key: value", 4, False, "raise") == ("a: 1", 1); n += 1
    assert node.run("{bad", "key: value", 4, False, "empty text") == ("", 0); n += 1
    assert "Invalid JSON" in _raises(node.run, "{bad", "key: value", 4, False, "raise"); n += 1
    return n
