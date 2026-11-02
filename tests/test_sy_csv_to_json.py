import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_csv_to_json as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    t = 'name,age,ok,note\nAnn,30,true,\nBob,2.5,False,"x, y"\n'
    js, c = m.table_to_json(t)
    assert c == 2; n += 1
    assert json.loads(js) == [{"name": "Ann", "age": 30, "ok": True, "note": ""},
                              {"name": "Bob", "age": 2.5, "ok": False, "note": "x, y"}]; n += 1
    assert "\n  " in js; n += 1
    js, _ = m.table_to_json(t, convert_numbers=False)
    assert json.loads(js)[0]["age"] == "30"; n += 1
    js, _ = m.table_to_json(t, shape="list of lists")
    assert json.loads(js)[1] == ["Bob", 2.5, False, "x, y"]; n += 1
    js, _ = m.table_to_json(t, shape="object of columns")
    assert json.loads(js)["age"] == [30, 2.5]; n += 1
    js, _ = m.table_to_json(t, indent=0)
    assert "\n" not in js; n += 1
    # no header
    js, c = m.table_to_json("1;2\n3;4", has_header=False)
    assert json.loads(js) == [{"col1": 1, "col2": 2}, {"col1": 3, "col2": 4}] and c == 2; n += 1
    # duplicate names, padding
    js, _ = m.table_to_json("a,a,a\n1")
    assert json.loads(js) == [{"a": 1, "a_2": "", "a_3": ""}]; n += 1
    # leading zeros stay text, unicode kept
    js, _ = m.table_to_json("id,w\n007,café")
    assert json.loads(js) == [{"id": "007", "w": "café"}] and "café" in js; n += 1
    assert m.convert_cell("-4") == -4 and m.convert_cell("abc") == "abc" and m.convert_cell("") == ""; n += 1
    # edge: header only, one data row, tab
    js, c = m.table_to_json("a,b")
    assert json.loads(js) == [] and c == 0; n += 1
    js, c = m.table_to_json("a\tb\n1\t2")
    assert c == 1 and json.loads(js) == [{"a": 1, "b": 2}]; n += 1
    # refusals
    assert "row 3" in _raises(m.table_to_json, "a,b\n1,2\n1,2,3"); n += 1
    assert "empty" in _raises(m.table_to_json, "  \n"); n += 1
    assert "shape" in _raises(m.table_to_json, "a", True, "auto", "weird"); n += 1
    assert "never closed" in _raises(m.table_to_json, 'a,"b'); n += 1
    assert "indent" in _raises(m.table_to_json, "a", True, "auto", "list of objects", True, 9); n += 1
    node = m.SYCsvToJson()
    assert node.run("a,b\n1,2", True, "auto", "list of objects", True, 0, "raise") == ('[{"a": 1, "b": 2}]', 1); n += 1
    assert node.run("", True, "auto", "list of objects", True, 2, "empty text") == ("", 0); n += 1
    assert "empty" in _raises(node.run, "", True, "auto", "list of objects", True, 2, "raise"); n += 1
    return n
