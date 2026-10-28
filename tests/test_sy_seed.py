import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_seed as m


def run():
    assert m.resolve_seed(5, "fixed") == 5
    assert m.resolve_seed(-3, "fixed") == 0
    assert m.resolve_seed(2 ** 70, "fixed") == m.MAX_SEED
    assert m.resolve_seed(5, "increment", None) == 5
    assert m.resolve_seed(5, "increment", 5) == 6
    assert m.resolve_seed(0, "increment", m.MAX_SEED) == 0
    r = {m.resolve_seed(0, "random") for _ in range(20)}
    assert len(r) > 1 and all(0 <= x <= m.MAX_SEED for x in r)
    try:
        m.resolve_seed(1, "bogus")
        raise SystemExit("bogus mode must raise")
    except ValueError:
        pass
    node = m.SYSeed()
    a = node.run(10, "increment", "n1")[0]
    b = node.run(10, "increment", "n1")[0]
    assert (a, b) == (10, 11), (a, b)
    assert node.run(7, "fixed", "n2") == (7,)
    return 9  # checks
