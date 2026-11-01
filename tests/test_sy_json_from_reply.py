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
    eq(m.SYJSONFromReply.RETURN_TYPES, ("STRING", "BOOLEAN", "STRING"))
    eq(m.json_from_reply('{"a": 1} then {"b": 2}', which="last"), ('{"b":2}', True))
    eq(m.json_from_reply('{"a": 1} then {"b": 2, "c": 3} and [1]', which="largest"), ('{"b":2,"c":3}', True))
    eq(m.json_from_reply('{"a": 1} then {"b": 2}', which="first"), ('{"a":1}', True))
    eq(m.json_from_reply('{"a": {"x": 1}} [5]', which="last"), ("[5]", True))
    eq(m.json_from_reply('{"a": [1]}', pretty=True), ('{\n  "a": [\n    1\n  ]\n}', True))
    eq(m.json_from_reply("{'a': True, 'b': None, 'c': 'x'}", python_style=True), ('{"a":true,"b":null,"c":"x"}', True))
    eq(m.json_from_reply("{'a': True}", raise_if_missing=False), ("", False))
    eq(m.json_from_reply("{'a': {1, 2}}", python_style=True, raise_if_missing=False), ("", False))
    eq(m.extract_blocks('x {"a": [1]} y [2] {bad} {"c": 3}'), [{"a": [1]}, [2], {"c": 3}])
    eq(m.extract_blocks('x {"a": [1]} y [2]', limit=1), [{"a": [1]}])
    eq(m.json_from_reply_info('{"a": 1, "b": 2}')[2], "Found an object with 2 keys (block 1 of 1).")
    eq(m.json_from_reply_info('{"a": 1} [1]', which="last")[2], "Found a list with 1 item (block 2 of 2).")
    eq(m.json_from_reply_info('{"a": 1} [1]')[2], "Found an object with 1 key (block 1 of 2).")
    eq(m.json_from_reply_info("nope", raise_if_missing=False), ("", False, "No JSON found in the text."))
    try:
        m.json_from_reply("{}", which="middle")
        raise SystemExit("bad which must raise")
    except ValueError:
        n += 1
    eq(m.SYJSONFromReply().run('see {"k": 1}', which="last"), ('{"k":1}', True, "Found an object with 1 key (block 1 of 1)."))
    eq(m.SYJSONFromReply.RETURN_NAMES, ("json_text", "found", "info"))
    return n
