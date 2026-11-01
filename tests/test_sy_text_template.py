import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_template as m


def raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.fill_template("a {x} and {y}", {"x": "1", "y": "2"}) == "a 1 and 2"; n += 1
    assert m.fill_template("{x}{x}", {"x": "ab"}) == "abab"; n += 1
    assert m.fill_template("no vars", {}) == "no vars"; n += 1
    assert m.fill_template("{x}", {"x": "{y}", "y": "no"}) == "{y}"; n += 1  # no second pass
    assert m.fill_template("json {1: 2}", {}) == "json {1: 2}"; n += 1
    assert m.fill_template("{x}", {"x": "1", "unused": "2"}) == "1"; n += 1
    assert raises(lambda: m.fill_template("{missing}", {"x": "1"})); n += 1
    assert raises(lambda: m.fill_template(5, {})); n += 1
    assert m.build_values([("a", "1"), ("", "z"), ("b", "2")]) == {"a": "1", "b": "2"}; n += 1
    assert raises(lambda: m.build_values([("a", "1"), ("a", "2")])); n += 1
    assert raises(lambda: m.build_values([("1bad", "1")])); n += 1
    node = m.SYTextTemplate()
    assert node.run("{p} in {q}", name_1="p", value_1="cat", name_2="q", value_2="rain")[0] == "cat in rain"; n += 1
    assert raises(lambda: node.run("{p}", name_1="q", value_1="x")); n += 1
    return n + _extra()


def _extra():
    n = 0
    assert m.fill_template("a {x} {y}", {"x": "1"}, "keep the {name} as it is") == "a 1 {y}"; n += 1
    assert m.fill_template("a {x} {y}", {"x": "1"}, "use empty text") == "a 1 "; n += 1
    assert raises(lambda: m.fill_template("{y}", {}, "stop with an error")); n += 1
    assert raises(lambda: m.fill_template("{y}", {}, "whatever")); n += 1
    text, info = m.template_report("{a} and {b}", {"a": "1", "b": "2"})
    assert text == "1 and 2" and info == "Filled 2 placeholder(s): a, b"; n += 1
    text, info = m.template_report("{a}", {"a": "1", "b": "2", "c": "3"})
    assert info == "Filled 1 placeholder(s): a; WARNING: input name(s) not used in the template: b, c"; n += 1
    text, info = m.template_report("{a} {z}", {"a": "1"}, "use empty text")
    assert text == "1 " and "1 without a value (left empty): {z}" in info; n += 1
    assert m.template_report("plain", {})[1] == "No {placeholders} in the template, so the text is unchanged"; n += 1
    out = m.SYTextTemplate().run("{p} {q}", name_1="p", value_1="cat", missing_mode="keep the {name} as it is")
    assert out[0] == "cat {q}" and "kept" in out[1]; n += 1
    assert m.SYTextTemplate.RETURN_NAMES == ("text", "info"); n += 1
    return n
