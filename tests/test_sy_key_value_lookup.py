import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_key_value_lookup as m


def run():
    n = 0
    t = "# heroes\nknight = a tall man in steel armour\n\n  Mage =  wise old wizard \nknight = second one\nurl = a=b"
    p = m.parse_table(t, "=")
    assert p[0] == ("knight", "a tall man in steel armour"); n += 1
    assert len(p) == 4; n += 1
    assert p[3] == ("url", "a=b"); n += 1   # only the first separator splits
    assert m.lookup(p, "KNIGHT", True, "") == ("a tall man in steel armour", True); n += 1   # first match wins
    assert m.lookup(p, "KNIGHT", False, "none") == ("none", False); n += 1
    assert m.lookup(p, " mage ", True, "") == ("wise old wizard", True); n += 1
    assert m.lookup(p, "zzz", True, "dflt") == ("dflt", False); n += 1
    assert m.parse_table("", "=") == []; n += 1
    assert m.parse_table("a -> b", "->") == [("a", "b")]; n += 1
    assert m.lookup([("k", "")], "k", True, "d") == ("", True); n += 1   # empty value still found
    for bad, sep, word in (("no separator here", "=", "line 1"), ("= value", "=", "no key"), ("a=b", "", "separator")):
        try:
            m.parse_table(bad, sep)
            raise SystemExit("bad table must raise")
        except ValueError as e:
            assert word in str(e), str(e)
            n += 1
    assert m.SYKeyValueLookup().run("a=1", "a") == ("1", True); n += 1
    return n
