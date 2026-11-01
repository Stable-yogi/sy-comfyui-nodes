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
    assert node.run(7, "fixed", "n2")[:1] == (7,)
    return 9 + _extra(m)


def _extra(m):
    n = 0
    def ok(c):
        assert c
        return 1
    def rs(fn, *a, **k):
        try:
            fn(*a, **k)
        except ValueError as e:
            return str(e)
        return None
    n += ok(m.resolve_seed(2 ** 60, 'fixed', None, '32-bit') == 2 ** 32 - 1)
    n += ok(m.resolve_seed(2 ** 60, 'fixed', None, '53-bit (browser safe)') == 2 ** 53 - 1)
    n += ok(m.resolve_seed(5, 'fixed', None, '64-bit') == m.resolve_seed(5, 'fixed'))
    n += ok(all(m.resolve_seed(0, 'random', None, '32-bit') <= 2 ** 32 - 1 for _ in range(50)))
    n += ok(m.resolve_seed(0, 'increment', 2 ** 32 - 1, '32-bit') == 0)
    n += ok(m.resolve_seed(5, 'increment', 5, '32-bit') == 6)
    n += ok('seed_range must be' in rs(m.resolve_seed, 1, 'fixed', None, 'huge'))
    n += ok(m.seed_info(5, 5, 'fixed') == ('5', 'seed 5 (fixed, 64-bit range)'))
    n += ok('did not fit' in m.seed_info(2 ** 40, 2 ** 32 - 1, 'fixed', '32-bit')[1])
    n += ok(m.SYSeed().run(9, 'fixed', 'n9', '32-bit') == (9, '9', 'seed 9 (fixed, 32-bit range)'))
    n += ok(m.SYSeed.IS_CHANGED(5, 'fixed', None, '32-bit') != m.SYSeed.IS_CHANGED(5, 'fixed', None, '64-bit'))
    return n
