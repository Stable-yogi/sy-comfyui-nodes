import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_wildcard_prompt as m


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def _boom(name):
    raise AssertionError("file must not be read")


def run():
    n = 0
    # plain text and pass-through of text without braces
    assert m.expand("a plain prompt", 1)[0] == "a plain prompt"; n += 1
    assert m.expand("", 1)[0] == ""; n += 1
    # same seed, same result; picks are reported
    t = "a {red|blue|green} coat, {sunrise|sunset}"
    a = m.expand(t, 42)
    assert a == m.expand(t, 42); n += 1
    assert a[0].startswith("a ") and len(a[1]) == 2; n += 1
    assert a[1][0].startswith("{red|blue|green} -> ") and a[1][0].split(" -> ")[1] in ("red", "blue", "green"); n += 1
    # different seeds differ, and every option shows up
    seen = set(m.expand("{red|blue|green}", s)[0] for s in range(60))
    assert seen == {"red", "blue", "green"}; n += 1
    assert len(set(m.expand(t, s)[0] for s in range(60))) > 3; n += 1
    # a huge seed works
    assert m.expand("{a|b}", 2 ** 64 - 1)[0] in ("a", "b"); n += 1
    # nesting
    nest = "{a|{b|c}}"
    assert set(m.expand(nest, s)[0] for s in range(80)) == {"a", "b", "c"}; n += 1
    assert m.possible_count(nest) == 3; n += 1
    assert m.expand("{{{{{x}}}}}", 0)[0] == "x"; n += 1
    # N$$ picks different options joined by comma
    for s in range(30):
        r = m.expand("{2$$a|b|c}", s)[0].split(", ")
        assert len(r) == 2 and r[0] != r[1] and set(r) <= {"a", "b", "c"}
    n += 1
    assert m.possible_count("{2$$a|b|c}") == 3; n += 1
    assert m.possible_count("{3$$a|b|c}") == 1 and m.expand("{3$$a|b|c}", 5)[0] == "a, b, c"; n += 1
    assert "asks to pick 4" in refuses(m.expand, "{4$$a|b|c}", 0); n += 1
    assert "pick 0" in refuses(m.expand, "{0$$a|b}", 0); n += 1
    # escapes
    assert m.expand("\\{a\\|b\\}", 0)[0] == "{a|b}"; n += 1
    assert m.expand("snake\\_case", 0)[0] == "snake_case"; n += 1
    assert m.expand("\\_\\_name\\_\\_", 0)[0] == "__name__"; n += 1
    assert m.expand("{a\\|b}", 0)[0] == "a|b"; n += 1
    assert m.expand("a | b", 0)[0] == "a | b"; n += 1
    # empty option is allowed when something else is in the list, spaces around options are trimmed
    assert set(m.expand("x{ big |}", s)[0] for s in range(40)) == {"xbig", "x"}; n += 1
    # wildcards
    wl = {"hair": ["red hair", "blonde hair"], "eyes": ["blue"]}
    r, picks = m.expand("a girl with __hair__ and __eyes__ eyes", 3, wl)
    assert "hair" in r and r.endswith("blue eyes"); n += 1
    assert picks[0].startswith("__hair__ -> ") and picks[1] == "__eyes__ -> blue"; n += 1
    assert m.expand("__HAIR__", 1, wl)[0] == m.expand("__hair__", 1, wl)[0]; n += 1
    assert set(m.expand("__hair__", s, wl)[0] for s in range(40)) == {"red hair", "blonde hair"}; n += 1
    assert m.expand("{__hair__|none}", 2, wl)[0] in ("red hair", "blonde hair", "none"); n += 1
    assert m.expand("__init and snake_case__", 0)[0] == "__init and snake_case__"; n += 1
    msg = refuses(m.expand, "__nope__", 0, wl)
    assert "nope" in msg and "eyes, hair" in msg; n += 1
    assert "empty" in refuses(m.expand, "__x__", 0, {"x": []}); n += 1
    assert m.describe("{a|b} __hair__ {c|d} __hair__") == (2, ["hair"]); n += 1
    assert m.possible_count("{a|b} __hair__", wl) == 4; n += 1
    # parse_wildcards
    p = m.parse_wildcards("# comment\nhair: red | blonde |  \n\nEyes : blue|green")
    assert p == {"hair": ["red", "blonde"], "eyes": ["blue", "green"]}; n += 1
    assert "line 1" in refuses(m.parse_wildcards, "just words"); n += 1
    assert "empty" in refuses(m.parse_wildcards, "x: | "); n += 1
    assert "no name" in refuses(m.parse_wildcards, ": a | b"); n += 1
    assert m.parse_wildcards("") == {}; n += 1
    # wildcard files (path guard, missing, empty)
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "wildcards"))
        with open(os.path.join(d, "wildcards", "mood.txt"), "w", encoding="utf-8") as f:
            f.write("# moods\nhappy\n\nsad\n")
        with open(os.path.join(d, "wildcards", "blank.txt"), "w", encoding="utf-8") as f:
            f.write("\n# nothing\n")
        assert m.load_wildcard_file(d, "mood") == ["happy", "sad"]; n += 1
        assert "'gone' was not found" in refuses(m.load_wildcard_file, d, "gone"); n += 1
        assert "empty" in refuses(m.load_wildcard_file, d, "blank"); n += 1
        assert "not allowed" in refuses(m.load_wildcard_file, d, "../../secret"); n += 1
        out = m.run_template("a __mood__ face", 1, m.MODES[0], 0, "", lambda nm: m.load_wildcard_file(d, nm))
        assert out[0] in ("a happy face", "a sad face") and "mood" in out[2]; n += 1
        # a list written in the box wins over the file and the file is not read
        out = m.run_template("__mood__", 1, m.MODES[0], 0, "mood: only", _boom)
        assert out[0] == "only"; n += 1
    # step through walks every combination once
    t2 = "{a|b} {c|d|e}"
    walk = [m.expand(t2, 0, None, i)[0] for i in range(6)]
    assert len(set(walk)) == 6 and set(walk) == {"%s %s" % (x, y) for x in "ab" for y in "cde"}; n += 1
    assert m.expand(t2, 0, None, 6)[0] == walk[0] and m.expand(t2, 0, None, 13)[0] == walk[1]; n += 1
    assert walk[0] == "a c" and walk[1] == "b c" and walk[2] == "a d"; n += 1
    # step through ignores the seed
    assert m.expand(t2, 1, None, 4) == m.expand(t2, 999, None, 4); n += 1
    # step through with nesting, N$$ and wildcards
    w3 = [m.expand("{x|{y|z}} __hair__", 0, wl, i)[0] for i in range(6)]
    assert len(set(w3)) == 6 and m.possible_count("{x|{y|z}} __hair__", wl) == 6; n += 1
    w4 = [m.expand("{2$$a|b|c}", 0, None, i)[0] for i in range(3)]
    assert sorted(w4) == ["a, b", "a, c", "b, c"]; n += 1
    # refusals
    assert "never closed" in refuses(m.expand, "a {b|c", 0); n += 1
    assert "no opening brace" in refuses(m.expand, "a b}", 0); n += 1
    assert "empty" in refuses(m.expand, "a {} b", 0) and "character 3" in refuses(m.expand, "a {} b", 0); n += 1
    assert "empty" in refuses(m.expand, "{|}", 0); n += 1
    assert "nested" in refuses(m.expand, "{a{b{c{d{e{f}}}}}}", 0); n += 1
    assert "line 2" in refuses(m.expand, "ok\n{}", 0); n += 1
    big = "{" + "|".join(["x" * 1200] * 2) + "}"
    assert "limit" in refuses(m.expand, big * 9, 0); n += 1
    assert m.expand(big * 8, 0)[0] == "x" * 9600; n += 1
    # counts
    assert m.possible_count("{a|b} {c|d|e} {f|g}") == 12; n += 1
    assert m.count_text(5) == "5" and m.count_text(2000000) == ">1000000"; n += 1
    assert m.possible_count("{a|b|c} " * 20) > 1000000; n += 1
    # run_template: info, picks, off, bad mode
    p, picks, info = m.run_template(t, 7, m.MODES[0], 0, "", None)
    assert "2 choice groups" in info and "seed 7" in info and "6 possible results" in info and picks.count("\n") == 1; n += 1
    p, picks, info = m.run_template(t2, 7, m.MODES[1], 3, "", None)
    assert "step 3" in info and p == walk[3]; n += 1
    off = m.run_template("{a|b} {", 1, m.MODES[0], 0, "", None, False)
    assert off == ("{a|b} {", "", "Wildcard Prompt: off, the text was passed through unchanged"); n += 1
    assert "mode must be" in refuses(m.run_template, "a", 1, "bogus", 0, "", None); n += 1
    assert "1 wildcard list used (hair)" in m.run_template("__hair__", 1, m.MODES[0], 0, "hair: a | b", None)[2]; n += 1
    # node class
    c = m.SYWildcardPrompt
    assert c.RETURN_NAMES == ("prompt", "picks", "info") and len(c.RETURN_TYPES) == 3; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYWildcardPrompt"] == "Wildcard Prompt SY"; n += 1
    spec = c.INPUT_TYPES()
    assert spec["required"]["seed"][1].get("control_after_generate") is True; n += 1
    assert c().run("a {b|b}", 1, m.MODES[0], "", 0, False)[0] == "a {b|b}"; n += 1
    return n
