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
    return n + _extra()


def _extra():
    n = 0
    assert m.estimate_info(2, 11, 4) == (False, "About 4 tokens (2 words, 11 characters); a CLIP text encoder reads this in 1 piece(s) of 75"); n += 1
    over, info = m.estimate_info(200, 900, 160, 77)
    assert over is True and "3 piece(s)" in info and "OVER your limit of 77 by about 83 tokens" in info; n += 1
    over, info = m.estimate_info(2, 11, 40, 77)
    assert over is False and info.endswith("within your limit of 77 (37 left)"); n += 1
    assert m.estimate_info(0, 0, 0)[1].endswith("in 0 piece(s) of 75"); n += 1
    out = m.SYTokenEstimate().run("word " * 100, 50)
    assert out[2] > 50 and out[3] is True and len(out) == 5; n += 1
    assert m.SYTokenEstimate().run("a b")[3] is False; n += 1
    assert m.SYTokenEstimate.RETURN_NAMES[-2:] == ("over_limit", "info"); n += 1
    return n
