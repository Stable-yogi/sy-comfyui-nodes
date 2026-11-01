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
        # added value
        with open(os.path.join(base, "bom.txt"), "wb") as f:
            f.write(b"\xef\xbb\xbfhi")
        assert m.read_text_file(base, "bom.txt") == "hi"; n += 1  # no byte order mark in the text
        with open(os.path.join(base, "list.txt"), "w", encoding="utf-8") as f:
            f.write("# header\n  one  \n\ntwo\n# note\nthree\n\n")
        assert m.load_text(base, "a.txt") == ("hello\nworld", 2, "2 lines, 11 characters."); n += 1
        text, count, info = m.load_text(base, "list.txt", 0, True, True)
        assert text == "one\n\ntwo\nthree" and count == 4 and "2 comment lines skipped" in info; n += 1
        text, count, info = m.load_text(base, "list.txt", 2, False, True)
        assert text == "" and count == 5; n += 1  # without strip the blank line is line 2 of the rest
        text, count, info = m.load_text(base, "list.txt", 1, True, True)
        assert text == "one" and info.startswith("Line 1 of 4."); n += 1
        assert m.load_text(base, "list.txt", 4, True, True)[0] == "three"; n += 1
        assert m.load_text(base, "list.txt", 1)[0] == "# header"; n += 1
        assert raises(m.load_text, base, "list.txt", 99); n += 1
        assert raises(m.load_text, base, "list.txt", -1); n += 1
        assert raises(m.load_text, base, "a.txt", 0, False, False, "sometimes"); n += 1
        assert m.load_text(base, "missing.txt", 0, False, False, "empty")[:2] == ("", 0); n += 1
        assert "Returning empty text" in m.load_text(base, "missing.txt", 0, False, False, "empty")[2]; n += 1
        assert raises(m.load_text, base, "missing.txt"); n += 1
        assert raises(m.load_text, base, "c.png", 0, False, False, "empty"); n += 1  # a wrong type is never silent
        assert raises(m.load_text, base, "../secret.txt", 0, False, False, "empty"); n += 1
        try:
            m.read_text_file(base, "lst.txt")
        except ValueError as e:
            assert "Close names in that folder: list.txt" in str(e)
            n += 1
        try:
            m.read_text_file(base, "nofolder/x.txt")
        except ValueError as e:
            assert "does not exist" in str(e)
            n += 1
        assert m.shape_text("", 0)[1] == 0; n += 1
        assert m.shape_text("a\n\n", 0, True)[0] == "a"; n += 1
        assert m.shape_text("a\r\nb", 2)[0] == "b"; n += 1
        out = m.SYLoadText.run(m.SYLoadText(), "x.txt") if False else None
    assert m.SYLoadText.RETURN_TYPES == ("STRING", "INT", "STRING"); n += 1
    assert m.SYLoadText.RETURN_NAMES == ("text", "line_count", "info"); n += 1
    spec = m.SYLoadText.INPUT_TYPES()
    assert list(spec["required"]) == ["file"] and list(spec["optional"]) == ["line", "strip", "skip_comments", "if_missing"]; n += 1
    v = m.SYLoadText.IS_CHANGED("x.txt", line=2)
    assert v != v; n += 1
    return n
