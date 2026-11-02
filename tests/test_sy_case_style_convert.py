import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_case_style_convert as m


def run():
    n = 0
    cases = [
        (("Hello big-world_test", "snake_case"), "hello_big_world_test"),
        (("Hello big-world_test", "kebab-case"), "hello-big-world-test"),
        (("Hello big-world_test", "camelCase"), "helloBigWorldTest"),
        (("hello big world", "PascalCase"), "HelloBigWorld"),
        (("helloBigWorld", "Title Case"), "Hello Big World"),
        (("helloBigWorld", "UPPER_SNAKE"), "HELLO_BIG_WORLD"),
        (("HTMLParser v2", "snake_case"), "html_parser_v_2"),
        (("item12 final!!", "kebab-case"), "item-12-final"),
        (("don't stop", "snake_case"), "dont_stop"),
        (("", "snake_case"), ""),
        (("  --  ", "camelCase"), ""),
        (("A", "PascalCase"), "A"),
    ]
    for args, want in cases:
        assert m.convert_case(*args) == want, (args, m.convert_case(*args))
        n += 1
    try:
        m.convert_case("x", "weird")
        raise SystemExit("bad style must raise")
    except ValueError as e:
        assert "style must be one of" in str(e)
        n += 1
    assert m.SYCaseStyleConvert().run("a b", "kebab-case") == ("a-b",)
    assert m.SYCaseStyleConvert.RETURN_TYPES == ("STRING",)
    return n + 2
