import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_json_from_reply as m


def run():
    n = 0

    def eq(got, want):
        nonlocal n
        assert got == want, "got %r, wanted %r" % (got, want)
        n += 1

    eq(m.json_from_reply('Sure! {"a": 1, "b": [1, 2]} done'), ('{"a":1,"b":[1,2]}', True))
    eq(m.json_from_reply('x [1, 2, 3] y'), ("[1,2,3]", True))
    eq(m.json_from_reply('{"a": 1, "b": [1, 2,],}'), ('{"a":1,"b":[1,2]}', True))
    eq(m.json_from_reply('{"a": "x}y,]", "b": 2}'), ('{"a":"x}y,]","b":2}', True))
    eq(m.json_from_reply('{"q": "say \\"hi}\\"", "z": 1}'), ('{"q":"say \\"hi}\\"","z":1}', True))
    eq(m.json_from_reply('{"b": 1, "a": 2}', sorted_keys=True), ('{"a":2,"b":1}', True))
    eq(m.json_from_reply('{"b": 1, "a": 2}'), ('{"b":1,"a":2}', True))
    eq(m.json_from_reply('{"a": 1} {"b": 2}'), ('{"a":1}', True))
    eq(m.json_from_reply('see [note] then {"k": true}'), ('{"k":true}', True))
    eq(m.json_from_reply('{"t": "a,}"}'), ('{"t":"a,}"}', True))
    eq(json.loads(m.json_from_reply('{"n": {"m": [1, {"x": null}]}}')[0]), {"n": {"m": [1, {"x": None}]}})
    eq(m.json_from_reply("no json here", raise_if_missing=False), ("", False))
    eq(m.json_from_reply("{broken", raise_if_missing=False), ("", False))
    for bad in ("no json here", "", "{broken: 1}"):
        try:
            m.json_from_reply(bad)
            raise SystemExit("missing json must raise")
        except ValueError:
            n += 1
    try:
        m.json_from_reply("x" * (m.MAX_INPUT + 1))
        raise SystemExit("too long input must raise")
    except ValueError:
        n += 1
    eq(m.SYJSONFromReply.RETURN_TYPES, ("STRING", "BOOLEAN"))
    return n
