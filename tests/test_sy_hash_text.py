import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_hash_text as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.hash_text("abc", "sha256", 0, False).startswith("ba7816bf"); n += 1
    assert len(m.hash_text("abc", "sha256", 0, False)) == 64; n += 1
    assert m.hash_text("abc", "md5", 0, False) == "900150983cd24fb0d6963f7d28e17f72"; n += 1
    assert m.hash_text("abc", "sha1", 0, False) == "a9993e364706816aba3e25717850c26c9cd0d89d"; n += 1
    assert len(m.hash_text("abc", "sha512", 0, False)) == 128; n += 1
    assert m.hash_text("abc", "sha256", 8, False) == "ba7816bf"; n += 1
    assert m.hash_text("abc", "md5", 128, False) == "900150983cd24fb0d6963f7d28e17f72"; n += 1
    assert m.hash_text("  abc\n", "md5", 0, True) == "900150983cd24fb0d6963f7d28e17f72"; n += 1
    assert m.hash_text("  abc\n", "md5", 0, False) != "900150983cd24fb0d6963f7d28e17f72"; n += 1
    assert m.hash_text("", "md5", 0, False) == "d41d8cd98f00b204e9800998ecf8427e"; n += 1
    assert m.hash_text("café", "sha256", 0, False) == m.hash_text("café", "sha256", 0, False); n += 1
    assert m.hash_text("café", "md5", 0, False) != m.hash_text("cafe", "md5", 0, False); n += 1
    d = m.hash_text("abc", "sha1", 5, False)
    assert d == d.lower() and len(d) == 5; n += 1
    msg = raises(m.hash_text, "abc", "crc32", 0, False)
    assert msg and "algorithm" in msg; n += 1
    msg = raises(m.hash_text, "abc", "md5", 129, False)
    assert msg and "length" in msg; n += 1
    assert raises(m.hash_text, "abc", "md5", -1, False); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYHashText"] == "Hash Text SY"; n += 1
    assert m.SYHashText.CATEGORY == "SY/Text"; n += 1
    return n
