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
    assert m.SYShortID().run(8, "hex", 5, "") == (a,)
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYShortID"] == "Short ID SY"
    return 11
