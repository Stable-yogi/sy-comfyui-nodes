import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_slugify as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.slugify("Hello World", "-", 0, True) == "hello-world"; n += 1
    assert m.slugify("Hello World", "_", 0, True) == "hello_world"; n += 1
    assert m.slugify("Hello World", "-", 0, False) == "Hello-World"; n += 1
    assert m.slugify("  --Hello,   World!!  ", "-", 0, True) == "hello-world"; n += 1
    assert m.slugify("café crème", "-", 0, True) == "cafe-creme"; n += 1
    assert m.slugify("naïve über", "_", 0, True) == "naive_uber"; n += 1
    assert m.slugify("a_b-c d", "-", 0, True) == "a-b-c-d"; n += 1
    assert m.slugify("a.b/c", "_", 0, True) == "a_b_c"; n += 1
    assert m.slugify("", "-", 0, True) == ""; n += 1
    assert m.slugify("!!!", "-", 0, True) == ""; n += 1
    assert m.slugify("Line one\nLine two", "-", 0, True) == "line-one-line-two"; n += 1
    assert m.slugify("hello world again", "-", 8, True) == "hello-wo"; n += 1
    assert m.slugify("hello world again", "-", 6, True) == "hello"; n += 1
    assert m.slugify("abc", "-", 2, True) == "ab"; n += 1
    assert m.slugify("Item 42", "-", 0, True) == "item-42"; n += 1
    assert m.slugify("中文", "-", 0, True) == ""; n += 1
    msg = raises(m.slugify, "x", "+", 0, True)
    assert msg and "separator" in msg; n += 1
    msg = raises(m.slugify, "x", "-", 300, True)
    assert msg and "max_length" in msg; n += 1
    assert raises(m.slugify, "x", "-", -1, True); n += 1
    assert raises(m.slugify, 5, "-", 0, True); n += 1
    assert m.SYSlugify().run("A B", "-", 0, True)[0] == "a-b"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSlugify"] == "Slugify SY"; n += 1
    return n + _extra()


def _extra():
    n = 0
    assert m.slugify("中文", "-", 0, True, "untitled") == "untitled"; n += 1
    assert m.slugify("中文", "_", 0, True, "My File") == "my_file"; n += 1
    assert m.slugify("ok", "-", 0, True, "untitled") == "ok"; n += 1
    assert m.slugify("!!!", "-", 0, True, "???") == ""; n += 1
    assert m.slugify("CON", "-", 0, True, "", True) == "con-file"; n += 1
    assert m.slugify("com1", "_", 0, True, "", True) == "com1_file"; n += 1
    assert m.slugify("console", "-", 0, True, "", True) == "console"; n += 1
    assert m.slugify("CON", "-", 0, True) == "con"; n += 1
    slug, info = m.slugify_info("中文", "-", 0, True)
    assert slug == "" and "WARNING" in info and "2 non-Latin" in info; n += 1
    slug, info = m.slugify_info("中文", "-", 0, True, "untitled")
    assert "used the fallback" in info and "untitled" in info; n += 1
    slug, info = m.slugify_info("hello world again", "-", 8, True)
    assert slug == "hello-wo" and "cut to max_length 8" in info; n += 1
    assert m.slugify_info("A B", "-", 0, True) == ("a-b", "Slug 'a-b' (3 characters)"); n += 1
    assert "empty" in m.slugify_info("", "-", 0, True)[1]; n += 1
    out = m.SYSlugify().run("", "-", 0, True, "untitled", False)
    assert out[0] == "untitled"; n += 1
    assert m.SYSlugify.RETURN_NAMES == ("slug", "info"); n += 1
    return n
