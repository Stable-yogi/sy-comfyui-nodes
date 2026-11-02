import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_escape_text as m


def run():
    n = 0
    e = m.escape_text
    assert e('a "q"\nb', "json string") == 'a \\"q\\"\\nb'; n += 1
    assert e('a \\"q\\"\\nb', "json string", "unescape") == 'a "q"\nb'; n += 1
    assert e("café", "json string") == "café"; n += 1
    assert e("a b&c/é", "url") == "a%20b%26c%2F%C3%A9"; n += 1
    assert e("a%20b%26c%2F%C3%A9", "url", "unescape") == "a b&c/é"; n += 1
    assert e("", "url") == "" and e("", "html") == "" and e("", "single line") == ""; n += 1
    assert e("l1\nl2\r\nl3", "single line") == "l1\\nl2\\nl3"; n += 1
    assert e("l1\\nl2", "single line", "unescape") == "l1\nl2"; n += 1
    tricky = "back\\slash and\\nreal\nline"
    assert e(e(tricky, "single line"), "single line", "unescape") == tricky; n += 1   # round trip
    assert e("<a href=\"x\">&'", "html") == "&lt;a href=&quot;x&quot;&gt;&amp;&#x27;"; n += 1
    assert e("&lt;b&gt; &amp;", "html", "unescape") == "<b> &"; n += 1
    for bad, mode, word in (("%zz", "url", "hex digits"), ("%C3%", "url", "hex digits"), ("%C3", "url", "valid text"),
                            ('a "unescaped', "json string", "not a valid JSON"), ("x", "weird", "mode must be"),
                            ("x", "url", "direction must be")):
        try:
            e(bad, mode, "bogus" if word == "direction must be" else "unescape")
            raise SystemExit("bad input must raise")
        except ValueError as ex:
            assert word in str(ex), str(ex)
            n += 1
    assert m.SYEscapeText().run("a\nb", "single line") == ("a\\nb",); n += 1
    return n
