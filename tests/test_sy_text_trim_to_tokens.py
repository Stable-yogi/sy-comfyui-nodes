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
    assert m.SYTextTrimToTokens().run(t, 2, "start") == ("01234567", 2, True); n += 1
    return n
