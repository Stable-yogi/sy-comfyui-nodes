import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_seed_list as m


def run():
    assert m.make_seeds(5, 3, "sequential") == [5, 6, 7]
    assert m.make_seeds(m.MAX_SEED, 2, "sequential") == [m.MAX_SEED, 0]
    a = m.make_seeds(42, 8, "random_fixed")
    assert a == m.make_seeds(42, 8, "random_fixed")
    assert a != m.make_seeds(43, 8, "random_fixed")
    assert len(set(a)) == 8 and all(0 <= x <= m.MAX_SEED for x in a)
    assert m.make_seeds(1, 64, "random_fixed")[:3] == m.make_seeds(1, 3, "random_fixed")
    for bad in ((1, 0, "sequential"), (1, 65, "sequential"), (1, 3, "bogus")):
        try:
            m.make_seeds(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError:
            pass
    text, first = m.SYSeedList().run(9, 3, "sequential")
    assert text == "9, 10, 11" and first == 9
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSeedList"] == "Seed List SY"
    return 10
