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
    return n
