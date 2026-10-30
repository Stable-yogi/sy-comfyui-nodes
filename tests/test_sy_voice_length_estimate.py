import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_voice_length_estimate as m


def run():
    n = 0
    words150 = " ".join(["word"] * 149) + " end."
    s, f, info = m.estimate(words150, "words", 150, 0.0, 0.0, 24, 16)
    assert s == 60.0 and f == 1441, (s, f); n += 1
    s, f, _ = m.estimate("one two three four five", "words", 150, 0.3, 0.5, 24, 16)
    assert s == 2.8 and f == 81, (s, f); n += 1  # 2.8*24=67.2 -> 5*16=80, +1
    s, f, _ = m.estimate("abc def", "characters", 60, 0.0, 0.0, 24, 16)
    assert s == 6.0, s; n += 1
    s2, _, _ = m.estimate("<d>[Japanese] Hello there</d>", "words", 150, 0.0, 0.0, 24, 16)
    s3, _, _ = m.estimate("Hello there", "words", 150, 0.0, 0.0, 24, 16)
    assert s2 == s3 == 0.8; n += 1
    a, _, _ = m.estimate("Hi. Yes! Ok?", "words", 150, 1.0, 0.0, 24, 16)
    b, _, _ = m.estimate("Hi. Yes! Ok?", "words", 150, 0.0, 0.0, 24, 16)
    assert round(a - b, 2) == 3.0; n += 1
    c, _, _ = m.estimate("Hi", "words", 150, 1.0, 0.0, 24, 16)
    assert round(c - 0.4, 2) == 1.0; n += 1  # no end mark still counts one sentence
    assert m.estimate("Hello", "words", 150, 0.0, 0.0, 24, 16)[1] == 17; n += 1
    assert m.estimate("Hello", "words", 150, 0.0, 0.5, 24, 16)[1] == 33; n += 1
    assert m.estimate("a - b", "words", 150, 0.0, 0.0, 24, 16)[2].startswith("2 words"); n += 1
    for bad in ("", "  ", "<d></d>", "[French]"):
        try:
            m.estimate(bad)
            raise SystemExit("blank must raise")
        except ValueError as e:
            assert "voice will say" in str(e)
        n += 1
    try:
        m.estimate("hi", "syllables")
        raise SystemExit("bad mode must raise")
    except ValueError:
        pass
    n += 1
    # video model grid: 17k + 5 (5, 22, 39 ...)
    assert m.estimate("Hello", "words", 150, 0.0, 0.0, 24, 17, 5)[1] == 22, m.estimate("Hello", "words", 150, 0.0, 0.0, 24, 17, 5); n += 1  # 9.6 -> 22
    assert m.estimate("Hello", "words", 150, 0.0, 0.0, 24, 17, 5)[1] % 17 == 5; n += 1
    s5, f5, _ = m.estimate("one two three four five", "words", 150, 0.3, 0.5, 24, 17, 5)
    assert s5 == 2.8 and f5 == 73 and f5 >= 67.2 and f5 % 17 == 5, (s5, f5); n += 1  # 17*4+5
    assert m.estimate("a", "words", 150, 0.0, 0.0, 1, 17, 5)[1] == 5; n += 1  # never below the offset
    try:
        m.estimate("hi", snap_offset=-1)
        raise SystemExit("negative offset must raise")
    except ValueError:
        pass
    n += 1
    assert m.SYVoiceLengthEstimate.RETURN_TYPES == ("FLOAT", "INT", "STRING"); n += 1
    return n
