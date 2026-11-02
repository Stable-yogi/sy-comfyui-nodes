import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_redact as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    r = m.redact
    assert r("Ann met Bob.", "Ann\nBob", "nothing", "[REDACTED]", "", True, True) == ("[REDACTED] met [REDACTED].", 2); n += 1
    assert r("Annual ann", "Ann", "nothing", "[REDACTED]", "", True, True) == ("Annual [REDACTED]", 1); n += 1
    assert r("Annual ann", "Ann", "nothing", "[REDACTED]", "", False, True) == ("[REDACTED]ual [REDACTED]", 2); n += 1
    assert r("ann Ann", "Ann", "nothing", "custom", "X", True, False) == ("ann X", 1); n += 1
    # longest phrase first
    assert r("I love New York", "New\nNew York", "nothing", "custom", "#", True, True) == ("I love #", 1); n += 1
    # styles
    assert r("hello", "hello", "nothing", "same length stars", "", True, True) == ("*****", 1); n += 1
    assert r("hi", "hi", "nothing", "block characters", "", True, True) == (m.BLOCK, 1); n += 1
    assert r("hi", "hi", "nothing", "custom", "", True, True) == ("", 1); n += 1
    # special characters are literal
    assert r("cost (a+b)", "(a+b)", "nothing", "custom", "?", True, True) == ("cost ?", 1); n += 1
    # patterns
    t = "Mail ann@example.com or call +1 (555) 123-4567, see https://example.com/a?b=1."
    out, c = r(t, "", "email addresses", "[REDACTED]", "", True, True)
    assert out == "Mail [REDACTED] or call +1 (555) 123-4567, see https://example.com/a?b=1." and c == 1; n += 1
    out, c = r(t, "", "phone-like numbers", "[REDACTED]", "", True, True)
    assert "[REDACTED]" in out and "555" not in out and c == 1; n += 1
    out, c = r(t, "", "web links", "[REDACTED]", "", True, True)
    assert out.endswith("see [REDACTED].") and c == 1; n += 1
    out, c = r(t, "", "all of these", "[REDACTED]", "", True, True)
    assert c == 3 and "@" not in out and "http" not in out; n += 1
    # overlapping hits count once
    assert r("ann@example.com", "ann@example.com", "email addresses", "[REDACTED]", "", True, True) == ("[REDACTED]", 1); n += 1
    # short digit runs are not phone-like
    assert r("room 12 and 345", "", "phone-like numbers", "[REDACTED]", "", True, True) == ("room 12 and 345", 0); n += 1
    # edge: empty text, empty words, blank lines, nothing to do
    assert r("", "x", "nothing", "[REDACTED]", "", True, True) == ("", 0); n += 1
    assert r("keep me", "", "nothing", "[REDACTED]", "", True, True) == ("keep me", 0); n += 1
    assert r("keep me", "\n  \n", "nothing", "[REDACTED]", "", True, True) == ("keep me", 0); n += 1
    assert r("x" * 10000, "x", "nothing", "[REDACTED]", "", False, True)[1] == 10000; n += 1
    # refusals
    assert "also_hide" in _raises(m.redact, "a", "", "emails", "[REDACTED]", "", True, True); n += 1
    assert "replace_with" in _raises(m.redact, "a", "", "nothing", "dots", "", True, True); n += 1
    assert "text" in _raises(m.redact, None, "", "nothing", "[REDACTED]", "", True, True); n += 1
    node = m.SYTextRedact()
    assert node.run("Hi Ann", "Ann", "nothing", "custom", "***", True, True) == ("Hi ***", 1); n += 1
    return n
