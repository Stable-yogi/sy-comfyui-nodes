import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_in_image as m


def _raises(*args):
    try:
        m.build_text_phrase(*args)
    except ValueError:
        return True
    return False


def run():
    f = m.build_text_phrase
    n = 0
    assert f("HELLO", "top") == 'Write the exact text "HELLO" at the top of the picture.'
    assert f("HELLO", "top", "bold red letters") == 'Write the exact text "HELLO" at the top of the picture, in bold red letters.'
    assert f("Hi", "centre", "", "German") == 'Write the exact text "Hi" in the centre of the picture. The text is in German.'
    assert f("Hi", "on_shirt").endswith("on the shirt.")
    assert f("Hi", "on_sign").endswith("on a sign in the scene.")
    assert f("Hi", "on_poster").endswith("on a poster in the scene.")
    n += 6
    for p in m.PLACEMENTS:
        assert '"Hi"' in f("Hi", p)
        n += 1
    assert f("  Hi  ", "left", " big, ").count("big") == 1
    assert _raises('say "hi"', "top")
    assert _raises("", "top")
    assert _raises("  ", "top")
    assert _raises("hi", "nowhere")
    assert m.SYTextInImage().run("A", "bottom")[0].startswith('Write the exact text "A"')
    return n + 6 + _extra()


def _extra():
    n = 0
    f = m.build_text_phrase
    assert f('say "hi"', "top", "", "", True) == "Write the exact text \"say 'hi'\" at the top of the picture."; n += 1
    assert f("\u201chi\u201d", "top", "", "", True).startswith('Write the exact text "\'hi\'"'); n += 1
    try:
        f('say "hi"', "top")
    except ValueError as e:
        assert "fix_quotes" in str(e); n += 1
    assert m.phrase_info("OPEN") == "1 word(s), 4 character(s) of picture text"; n += 1
    assert "WARNING" in m.phrase_info("this is a rather long sentence for a sign"); n += 1
    assert "language_hint" in m.phrase_info("Gr\u00fc\u00dfe"); n += 1
    assert "language_hint" not in m.phrase_info("Gr\u00fc\u00dfe", "German"); n += 1
    assert "capital letters" in m.phrase_info("open"); n += 1
    out = m.SYTextInImage().run('a "b"', "top", "", "", True)
    assert out[0].startswith("Write the exact text") and out[1].startswith("2 word(s)"); n += 1
    assert m.SYTextInImage.RETURN_NAMES == ("phrase", "info"); n += 1
    return n
