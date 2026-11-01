import hashlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_seed_from_text as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.seed_from_text("hello", 0) == 3383668851506584; n += 1
    assert m.seed_from_text("hello", 1) == 7528443221043741; n += 1
    assert m.seed_from_text("", 0) == 6345501181504748; n += 1
    assert m.seed_from_text("Stable Yogi", 7) == 1380475751025000; n += 1
    assert m.seed_from_text("hello", 0) == m.seed_from_text("hello", 0); n += 1
    assert m.seed_from_text("hello", 0) != m.seed_from_text("hello", 1); n += 1
    assert m.seed_from_text("hello", 0) != m.seed_from_text("Hello", 0); n += 1
    assert m.seed_from_text("hello") == m.seed_from_text("hello", 0); n += 1
    d = hashlib.sha256(b"0:hello").digest()
    assert m.seed_from_text("hello", 0) == int.from_bytes(d[:8], "big") % (2 ** 53); n += 1
    for t in ("", "a", "tiny", "café ☃", "x" * 5000):
        assert 0 <= m.seed_from_text(t, 2 ** 32 - 1) < 2 ** 53; n += 1
    assert m.seed_from_text("café", 3) == m.seed_from_text("café", 3); n += 1
    msg = raises(m.seed_from_text, "a", -1)
    assert msg and "salt" in msg; n += 1
    assert raises(m.seed_from_text, "a", 2 ** 32); n += 1
    assert raises(m.seed_from_text, "a", 1.5); n += 1
    assert raises(m.seed_from_text, 5, 0); n += 1
    assert m.SYSeedFromText().run("hello", 0)[:1] == (3383668851506584,); n += 1
    assert m.SYSeedFromText.CATEGORY.endswith("Values"); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSeedFromText"] == "Seed From Text SY"; n += 1
    return n + _extra(m)


def _extra(m):
    n = 0
    def ok(c):
        assert c
        return 1
    def rs(fn, *a, **k):
        try:
            fn(*a, **k)
        except ValueError as e:
            return str(e)
        return None
    n += ok(m.seed_from_text('Cat ', 0, True) == m.seed_from_text('cat', 0, True))
    n += ok(m.seed_from_text('Cat ', 0) != m.seed_from_text('cat', 0))
    n += ok(m.seed_from_text('hello', 3, False) == m.seed_from_text('hello', 3))
    n += ok(m.seed_from_text('a  b', 0, True) == m.seed_from_text('A b', 0, True))
    n += ok('case and spaces ignored' in m.seed_from_text_info('X', 0, True))
    n += ok(m.seed_from_text_info('hello', 0).startswith('seed 3383668851506584 from'))
    n += ok('...' in m.seed_from_text_info('x' * 80, 0))
    n += ok(m.SYSeedFromText().run('Cat', 0, True)[0] == m.SYSeedFromText().run('cat ', 0, True)[0])
    return n
