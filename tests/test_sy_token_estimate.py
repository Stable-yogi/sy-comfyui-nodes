import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_token_estimate as m


def run():
    n = 0
    assert m.estimate_tokens("") == (0, 0, 0); n += 1
    w, c, t = m.estimate_tokens("hello world")
    assert (w, c) == (2, 11); n += 1
    assert 2 <= t <= 6; n += 1
    w, c, t = m.estimate_tokens("one  two\nthree")
    assert w == 3; n += 1
    short = m.estimate_tokens("word")[2]
    long = m.estimate_tokens("word " * 100)[2]
    assert long > short >= 1; n += 1
    assert 100 <= m.estimate_tokens("word " * 100)[2] <= 250; n += 1
    try:
        m.estimate_tokens(None)
        raise SystemExit("bad args must raise")
    except ValueError:
        n += 1
    assert m.SYTokenEstimate().run("a b")[0] == 2; n += 1
    assert "estimate" in m.SYTokenEstimate.DESCRIPTION; n += 1
    return n
