import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_tag_frequency as m


def bad(*args):
    try:
        m.frequency_report(*args)
    except ValueError as e:
        return str(e)
    raise SystemExit("must raise: %r" % (args,))


def run():
    text = "dog, grass, Sunny\ncat, grass\n\ndog,  grass , dog\n"
    n, counts = m.count_tags(text)
    assert n == 3                                      # blank line is not a caption
    assert counts == {"dog": 2, "grass": 3, "sunny": 1, "cat": 1}      # dog twice in a line counts once
    assert m.count_tags(text, ",", False)[1]["Sunny"] == 1
    assert "sunny" not in m.count_tags(text, ",", False)[1]
    assert m.count_tags("a|b|a", "|")[1] == {"a": 1, "b": 1}
    assert m.count_tags("a,,b, ,")[1] == {"a": 1, "b": 1}              # empty tags dropped
    assert m.count_tags("big   dog")[1] == {"big dog": 1}               # inner spaces tidied
    rep, uniq = m.frequency_report(text)
    assert uniq == 4
    lines = rep.split("\n")
    assert lines[0] == "captions: 3" and lines[1] == "different tags: 4"
    assert lines[3:] == ["3  grass", "2  dog", "1  cat", "1  sunny"]     # by count, then by name
    rep, uniq = m.frequency_report(text, ",", True, 2)
    assert rep.split("\n")[4:] == ["3  grass", "2  dog"] and uniq == 4 and "showing: 2" in rep
    rep, _ = m.frequency_report(text, ",", True, 1, 1)
    assert rep.split("\n")[4:] == ["3  grass"]
    assert "no captions" in bad("  \n\n", ",", True, 1, 0)
    assert "no captions" in bad("", ",", True, 1, 0)
    assert "separator" in bad("a", "", True, 1, 0)
    assert "min_count" in bad("a", ",", True, 0, 0)
    assert "top_n" in bad("a", ",", True, 1, -1)
    assert m.SYTagFrequency().run("a, b\na", ",", True, 1, 0)[1] == 2
    return 16 + _extra()


def _extra():
    n = 0
    caps = "ohwx, dog, grass\ndog, ohwx, grass\ncat, grass, grass\n\nOHWX, watermark text, Dog"
    txt, c = m.caption_problems(caps, ",", True, "ohwx", "watermark")
    assert c == 4, txt; n += 1
    assert "Same tag twice in one caption (1 caption(s)): line 3: grass" in txt; n += 1
    assert "Trigger word 'ohwx' is missing in 1 caption(s): lines 3" in txt; n += 1
    assert "not the first tag in 1 caption(s): lines 2" in txt; n += 1
    assert "Banned word 'watermark' found in 1 caption(s): lines 5" in txt; n += 1
    assert m.caption_problems("a, b\nc, d") == ("No problems found in 2 caption(s)", 0); n += 1
    assert m.caption_problems("  \n") == ("No captions to check: put one caption on each line", 0); n += 1
    assert m.caption_problems("a, A", ",", True)[1] == 1; n += 1
    assert m.caption_problems("a, A", ",", False)[1] == 0; n += 1
    assert m.caption_problems("a cat, b", ",", True, "", "cat")[1] == 1; n += 1
    assert m.caption_problems("concatenate, b", ",", True, "", "cat")[1] == 0; n += 1
    assert m.caption_problems("ohwx, a", ",", True, "OHWX")[1] == 0; n += 1
    many = "\n".join("x" for _ in range(12))
    assert "... (4 more)" in m.caption_problems(many, ",", True, "ohwx")[0]; n += 1
    try:
        m.caption_problems("a", "")
        raise SystemExit("empty separator must raise")
    except ValueError:
        n += 1
    out = m.SYTagFrequency().run("a, b\nb, a", ",", True, 1, 0, "a", "")
    assert len(out) == 4 and out[1] == 2 and out[3] == 1 and "not the first" in out[2]; n += 1
    assert m.SYTagFrequency.RETURN_NAMES[-2:] == ("problems", "problem_count"); n += 1
    return n
