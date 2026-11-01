import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_short_id as m


def run():
    a = m.make_id(8, "hex", 5)
    assert a == m.make_id(8, "hex", 5) and a != m.make_id(8, "hex", 6)
    assert len(a) == 8 and set(a) <= set(m.CHARSETS["hex"])
    assert m.make_id(12, "letters", 1).isalpha()
    assert m.make_id(16, "digits", 1).isdigit()
    assert set(m.make_id(16, "mixed", 1)) <= set(m.CHARSETS["mixed"])
    p = m.make_id(6, "hex", 5, "run_")
    assert p.startswith("run_") and len(p) == 10
    for bad in ((3, "hex", 1), (17, "hex", 1), (8, "bogus", 1)):
        try:
            m.make_id(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError:
            pass
    assert m.SYShortID().run(8, "hex", 5, "")[:1] == (a,)
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYShortID"] == "Short ID SY"
    # --- value pass A2: readable set, new code each run, info line
    n = 11
    r = m.make_id(16, "readable", 3)
    assert set(r) <= set(m.CHARSETS["readable"]) and not set(r) & set("01oli"); n += 1
    assert m.make_id(8, "hex", 5, "", 1) == m.make_id(8, "hex", 5, "", 1) and m.make_id(8, "hex", 5, "", 1) != m.make_id(8, "hex", 5, "", 2); n += 1
    assert m.make_id(8, "hex", 5, "", None) == a; n += 1
    i = m.id_info("ab12", 4, "hex", 5, "", False)
    assert i == "ab12: from seed 5 (same seed, same code), hex, 4 characters, about 65,536 possible codes"; n += 1
    assert "new code every run" in m.id_info("ab12", 4, "hex", 5, "", True); n += 1
    assert "not allowed in file names" in m.id_info("a/b1", 4, "hex", 5, "a/", False) and "Warning" not in m.id_info("run_ab", 4, "hex", 5, "run_", False); n += 2
    code, info = m.SYShortID().run(8, "hex", 5, "x_", False)
    assert code == "x_" + a and info.startswith(code); n += 1
    c1, c2 = m.SYShortID().run(8, "hex", 5, "", True)[0], m.SYShortID().run(8, "hex", 5, "", True)[0]
    assert len(c1) == 8 and c1 != c2; n += 1
    assert m.SYShortID.IS_CHANGED(new_each_run=True) != m.SYShortID.IS_CHANGED(new_each_run=True) and m.SYShortID.IS_CHANGED() == ""; n += 1
    assert m.SYShortID.RETURN_NAMES == ("short_id", "info"); n += 1
    return n
