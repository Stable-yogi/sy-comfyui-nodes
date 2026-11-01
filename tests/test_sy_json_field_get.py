import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_json_field_get as m

DOC = '{"a": {"b": [10, {"c": "deep"}, [1, 2]]}, "t": true, "n": null, "s": "text", "7": "digits"}'


def run():
    n = 0
    assert m.get_field(DOC, "a.b.0") == "10"; n += 1
    assert m.get_field(DOC, "a.b.1.c") == "deep"; n += 1
    assert m.get_field(DOC, "a.b.2") == "[1, 2]"; n += 1
    assert m.get_field(DOC, "a.b.-1.1") == "2"; n += 1
    assert m.get_field(DOC, "t") == "true" and m.get_field(DOC, "n") == "null"; n += 1
    assert m.get_field(DOC, "s") == "text" and m.get_field(DOC, "7") == "digits"; n += 1
    assert m.get_field(DOC, "a.b.1") == '{"c": "deep"}'; n += 1
    assert m.get_field('{"x": 1}', "") == '{"x": 1}'; n += 1
    for path in ("zzz", "a.zzz", "a.b.9", "a.b.x", "a..b", "s.x", "a.b.1.c.d"):
        try:
            m.get_field(DOC, path)
            raise SystemExit("bad path must raise: " + path)
        except ValueError:
            n += 1
    for call in (lambda: m.get_field("{bad", "a"), lambda: m.get_field("", "a"), lambda: m.get_field(3, "a"), lambda: m.get_field("{}", 3)):
        try:
            call()
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert m.SYJSONFieldGet().run(DOC, "a.b.0") == ("10", True, "number"); n += 1
    assert m.get_field_ex(DOC, "nope", "fallback") == ("fallback", False, "default"); n += 1
    assert m.get_field_ex(DOC, "nope", "") == ("", False, "default"); n += 1
    assert m.get_field_ex(DOC, "a.b.9", "x")[1] is False; n += 1
    assert m.get_field_ex(DOC, "a.b.0", "x") == ("10", True, "number"); n += 1
    assert [m.get_field_ex(DOC, p)[2] for p in ("s", "t", "n", "a.b", "a")] == ["text", "true/false", "empty", "list", "object"]; n += 1
    assert m.get_field_ex('```json\n{"k": 5}\n```', "k") == ("5", True, "number"); n += 1
    assert m.get_field_ex('```\n{"k": "v"}', "k") == ("v", True, "text"); n += 1
    for call in (lambda: m.get_field_ex("{bad", "a", "x"), lambda: m.get_field_ex("{}", "..b", "x"), lambda: m.get_field_ex("```\n{bad\n```", "a")):
        try:
            call()
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    assert m.SYJSONFieldGet().run(DOC, "zzz", "use default", "none") == ("none", False, "default"); n += 1
    assert m.SYJSONFieldGet().run(DOC, "a.b.0", "use default", "none")[1] is True; n += 1
    try:
        m.SYJSONFieldGet().run(DOC, "zzz", "error", "none")
        raise SystemExit("must raise")
    except ValueError:
        n += 1
    assert m.SYJSONFieldGet.RETURN_NAMES == ("value", "found", "kind"); n += 1
    return n
