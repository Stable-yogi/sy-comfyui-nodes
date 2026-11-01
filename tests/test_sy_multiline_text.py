import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_multiline_text as m


def run():
    n = 0
    f = m.strip_comments
    assert f("a\n# note\nb") == "a\nb"; n += 1
    assert f("a\n   # indented note\nb") == "a\nb"; n += 1
    assert f("a # not a comment") == "a # not a comment"; n += 1
    assert f("\\# keep") == "# keep"; n += 1
    assert f("a\n\nb") == "a\n\nb"; n += 1
    assert f("a\n\nb", keep_empty_lines=False) == "a\nb"; n += 1
    assert f("# only") == ""; n += 1
    assert f("") == ""; n += 1
    assert f("a\r\n#c\r\nb") == "a\nb"; n += 1
    try:
        f(None)
        raise SystemExit("bad args must raise")
    except ValueError:
        n += 1
    assert m.SYMultilineText().run("x\n#y") == ("x", 1, "Kept 1 of 2 lines (1 left out).") ; n += 1
    g = m.clean_lines
    assert g("a\n#c\nb") == "a\nb"; n += 1
    assert g("  a  b  \n#c") == "  a  b  "; n += 1
    assert g("  a  b  ", trim_lines=True) == "a  b"; n += 1
    assert g("  a  b  ", collapse_spaces=True) == " a b "; n += 1
    assert g("  a  b  ", trim_lines=True, collapse_spaces=True) == "a b"; n += 1
    assert g("a\nA\nb\n\n\nB\n a ", drop_duplicate_lines=True) == "a\nb\n\n"; n += 1
    assert g("a\nb\n", drop_duplicate_lines=True) == "a\nb\n"; n += 1
    assert g("a cat # old\n  # note\nb#c", inline_comments=True) == "a cat\nb#c"; n += 1
    assert g("x # y\n\\# keep", inline_comments=True) == "x\n# keep"; n += 1
    assert g("  \\# keep", inline_comments=True) == "  # keep"; n += 1
    assert g("a\n\nb", False, drop_duplicate_lines=True) == "a\nb"; n += 1
    assert g("") == ""; n += 1
    assert m.lines_info("a\nb", "a\nb") == (2, "Kept all 2 lines."); n += 1
    assert m.lines_info("a", "a") == (1, "Kept all 1 line."); n += 1
    assert m.lines_info("#a\nb\nc", "b\nc") == (2, "Kept 2 of 3 lines (1 left out)."); n += 1
    assert m.lines_info("#a", "") == (0, "Kept 0 of 1 lines (1 left out)."); n += 1
    assert m.lines_info("", "") == (0, "Kept all 0 lines."); n += 1
    assert m.SYMultilineText().run("a\nA", True, False, False, True) == ("a", 1, "Kept 1 of 2 lines (1 left out)."); n += 1
    assert m.SYMultilineText.RETURN_NAMES == ("text", "line_count", "info"); n += 1
    return n
