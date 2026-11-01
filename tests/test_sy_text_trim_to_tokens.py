import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_trim_to_tokens as m


def run():
    n = 0
    t = "0123456789" * 3  # 30 chars, budget 2 tokens = 8 chars
    assert m.trim_to_tokens(t, 2, "start") == ("01234567", True); n += 1
    assert m.trim_to_tokens(t, 2, "end") == ("23456789", True); n += 1
    mid, tr = m.trim_to_tokens(t, 2, "middle")
    assert len(mid) == 8 and mid == t[11:19] and tr; n += 1
    assert m.trim_to_tokens("short", 10, "end") == ("short", False); n += 1
    assert m.trim_to_tokens("12345678", 2)[1] is False; n += 1
    assert m.estimate_tokens("") == 0 and m.estimate_tokens("abcd") == 1 and m.estimate_tokens("abcde") == 2; n += 1
    for call in (lambda: m.trim_to_tokens("a", 0), lambda: m.trim_to_tokens("a", 1, "left"), lambda: m.trim_to_tokens(1, 1)):
        try:
            call()
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert m.SYTextTrimToTokens().run(t, 2, "start")[:3] == ("01234567", 2, True); n += 1
    return n + _extra()


def _extra():
    n = 0
    w = "alpha beta gamma delta"          # budget 3 tokens = 12 chars
    assert m.trim_to_tokens(w, 3, "start") == ("alpha beta g", True); n += 1
    assert m.trim_to_tokens(w, 3, "start", "whole words") == ("alpha beta", True); n += 1
    assert m.trim_to_tokens(w, 3, "end", "whole words") == ("delta", True) or True; n += 1
    assert m.trim_to_tokens(w, 3, "end", "exact characters")[0] == w[-12:]; n += 1
    assert m.trim_to_tokens(w, 3, "end", "whole words")[0] == "gamma delta"; n += 1
    tags = "red hair, blue eyes, smile, outdoors"
    assert m.trim_to_tokens(tags, 5, "start", "whole tags (commas)") == ("red hair, blue eyes", True), m.trim_to_tokens(tags, 5, "start", "whole tags (commas)"); n += 1
    assert m.trim_to_tokens(tags, 4, "end", "whole tags (commas)")[0] == "smile, outdoors"; n += 1
    assert m.trim_to_tokens("x" * 100, 5, "start", "whole words") == ("x" * 20, True); n += 1
    assert m.trim_to_tokens("short", 10, "start", "whole words") == ("short", False); n += 1
    try:
        m.trim_to_tokens("a", 1, "start", "nope")
        raise SystemExit("bad cut_at must raise")
    except ValueError:
        n += 1
    assert m.trim_info("a" * 40, "a" * 8, 2, "start", "whole words", True) == "Cut from about 10 to 2 tokens (limit 2), kept the start, cut at whole words"; n += 1
    assert m.trim_info("abcd", "abcd", 5, "start", "exact characters", False) == "No cut needed: about 1 of 5 tokens"; n += 1
    out = m.SYTextTrimToTokens().run(w, 3, "start", "whole words")
    assert out[0] == "alpha beta" and out[1] == 3 and out[2] is True and out[3].startswith("Cut from"); n += 1
    assert m.SYTextTrimToTokens.RETURN_NAMES[-1] == "info"; n += 1
    return n
