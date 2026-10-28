import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_load_text as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "in")
        os.makedirs(os.path.join(base, "sub"))
        with open(os.path.join(base, "a.txt"), "w", encoding="utf-8") as f:
            f.write("hello\nworld")
        with open(os.path.join(base, "sub", "b.TXT"), "w", encoding="utf-8") as f:
            f.write("deep")
        with open(os.path.join(base, "c.png"), "w") as f:
            f.write("x")
        with open(os.path.join(tmp, "secret.txt"), "w") as f:
            f.write("no")
        assert m.read_text_file(base, "a.txt") == "hello\nworld"; n += 1
        assert m.read_text_file(base, "sub/b.TXT") == "deep"; n += 1
        assert m.read_text_file(base, "sub\\b.TXT") == "deep"; n += 1
        for bad in ("c.png", "", "missing.txt", "../secret.txt", "..\\secret.txt", "sub/../../secret.txt",
                    "C:\\secret.txt", "/etc/passwd.txt", "\\\\host\\share\\x.txt", os.path.join(tmp, "secret.txt")):
            assert raises(m.read_text_file, base, bad), bad; n += 1
        old = m.MAX_BYTES
        m.MAX_BYTES = 3
        try:
            assert raises(m.read_text_file, base, "a.txt"); n += 1
        finally:
            m.MAX_BYTES = old
    assert m.SYLoadText.RETURN_TYPES == ("STRING",); n += 1
    return n
