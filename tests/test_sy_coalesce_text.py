import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_coalesce_text as m


def run():
    n = 0
    c = m.coalesce
    assert c(["a", "b"]) == ("a", 1); n += 1
    assert c(["", "b", "c"]) == ("b", 2); n += 1
    assert c(["  \n", None, "c"]) == ("c", 3); n += 1
    assert c(["  ", "b"], False) == ("  ", 1); n += 1   # spaces count as text when told so
    assert c(["", None, " "], True, "dflt") == ("dflt", 0); n += 1
    assert c([], True, "x") == ("x", 0); n += 1
    assert c(["", "", "", "", "last"]) == ("last", 5); n += 1
    assert c([" keep spaces "]) == (" keep spaces ", 1); n += 1   # value is not trimmed
    try:
        c(["", 5])
        raise SystemExit("non text must raise")
    except ValueError as e:
        assert "slot 2" in str(e)
        n += 1
    node = m.SYCoalesceText()
    assert node.run("", None, "x") == ("x", 3); n += 1
    assert node.run("", fallback="f") == ("f", 0); n += 1
    assert list(m.SYCoalesceText.INPUT_TYPES()["required"]) == ["text_1"]; n += 1
    return n
