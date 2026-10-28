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
    assert node.run("{p} in {q}", name_1="p", value_1="cat", name_2="q", value_2="rain") == ("cat in rain",); n += 1
    assert raises(lambda: node.run("{p}", name_1="q", value_1="x")); n += 1
    return n
