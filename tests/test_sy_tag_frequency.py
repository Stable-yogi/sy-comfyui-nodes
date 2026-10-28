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
    return 16
