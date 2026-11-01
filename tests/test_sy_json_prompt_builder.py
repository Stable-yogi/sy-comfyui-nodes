import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_json_prompt_builder as m


def run():
    n = 0
    out = m.build_json("subject: a fox\nsteps: 20\nscale=7.5\nhd: true\nnone: null", True, 0)
    assert json.loads(out) == {"subject": "a fox", "steps": 20, "scale": 7.5, "hd": True, "none": None}; n += 1
    assert "\n" not in out; n += 1
    assert json.loads(m.build_json("steps: 20\nhd: true", False)) == {"steps": "20", "hd": "true"}; n += 1
    tricky = 'quote: say "hi"\\there\nurl: http://x.y/a:b\nuni: caf\u00e9'
    d = json.loads(m.build_json(tricky))
    assert d["quote"] == 'say "hi"\\there' and d["url"] == "http://x.y/a:b" and d["uni"] == "caf\u00e9"; n += 1
    assert json.loads(m.build_json("# note\n\n a : b ")) == {"a": "b"}; n += 1
    assert "\n  " in m.build_json("a: b", True, 2); n += 1
    assert json.loads(m.build_json("v: nan"))["v"] == "nan"; n += 1
    for call in (lambda: m.build_json("no separator"), lambda: m.build_json(": v"), lambda: m.build_json("a: 1\na: 2"),
                 lambda: m.build_json("\n# only comment"), lambda: m.build_json("a: b", True, 9), lambda: m.build_json(5)):
        try:
            call()
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert json.loads(m.SYJSONPromptBuilder().run("a: 1", True, 2)[0]) == {"a": 1}; n += 1
    assert json.loads(m.build_json("cam.angle: low\ncam.lens: 35\nmood: calm", True, 0, True)) == {"cam": {"angle": "low", "lens": 35}, "mood": "calm"}; n += 1
    assert json.loads(m.build_json("cam.angle: low", True, 0, False)) == {"cam.angle": "low"}; n += 1
    assert json.loads(m.build_json("a.b.c: 1", True, 0, True)) == {"a": {"b": {"c": 1}}}; n += 1
    assert json.loads(m.build_json("tags: fox | red | 3\nsolo: one", True, 0, False, "|")) == {"tags": ["fox", "red", 3], "solo": "one"}; n += 1
    assert json.loads(m.build_json("tags: 1 | 2", False, 0, False, "|")) == {"tags": ["1", "2"]}; n += 1
    assert json.loads(m.build_json("t: a, b", True, 0, False, "|")) == {"t": "a, b"}; n += 1
    for call in (lambda: m.build_json("a: 1\na.b: 2", True, 0, True), lambda: m.build_json("a.b: 2\na: 1", True, 0, True),
                 lambda: m.build_json("a.b: 1\na.b: 2", True, 0, True), lambda: m.build_json("a..b: 1", True, 0, True)):
        try:
            call()
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    assert m.json_info({"a": 1, "b": True, "c": None, "d": [1], "e": {"f": 2.5}}) == "6 keys (2 numbers, 1 true/false, 1 list, 1 group, 1 empty)."; n += 1
    assert m.json_info({"a": "x"}) == "1 key."; n += 1
    assert m.json_info({"a": 1}) == "1 key (1 number)."; n += 1
    assert m.SYJSONPromptBuilder().run("a: 1\nb: x", True, 0)[1] == "2 keys (1 number)."; n += 1
    assert m.SYJSONPromptBuilder().run("a.b: 1", True, 0, True) == ('{"a": {"b": 1}}', "2 keys (1 number, 1 group)."); n += 1
    assert m.SYJSONPromptBuilder.RETURN_NAMES == ("json", "info"); n += 1
    return n
