import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_size_snap as m


def _raises(*args):
    try:
        m.snap_size(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.snap_size(1000, 1000, 8, "nearest") == (1000, 1000); n += 1
    assert m.snap_size(1001, 1003, 8, "nearest") == (1000, 1000); n += 1
    assert m.snap_size(1005, 1007, 8, "nearest") == (1008, 1008); n += 1
    assert m.snap_size(1004, 1004, 8, "nearest") == (1008, 1008); n += 1  # exact half goes up
    assert m.snap_size(1001, 1001, 8, "up") == (1008, 1008); n += 1
    assert m.snap_size(1008, 1008, 8, "up") == (1008, 1008); n += 1
    assert m.snap_size(1007, 1015, 8, "down") == (1000, 1008); n += 1
    assert m.snap_size(3, 5, 8, "down") == (8, 8); n += 1  # never below one multiple
    assert m.snap_size(1, 1, 1, "nearest") == (1, 1); n += 1
    assert m.snap_size(5, 5, 3, "nearest") == (6, 6); n += 1  # odd multiple
    assert m.snap_size(4, 4, 3, "nearest") == (3, 3); n += 1
    assert m.snap_size(1500, 1501, 1, "up") == (1500, 1501); n += 1
    assert m.snap_size(65535, 65535, 64, "up") == (65536, 65536); n += 1  # huge
    for bad in ((0, 5, 8, "up"), (5, 0, 8, "up"), (5, 5, 0, "up"), (5, 5, 8, "sideways"), (-4, 5, 8, "nearest")):
        assert _raises(*bad), bad
        n += 1
    assert m.SYSizeSnap().run(1001, 1001, 8, "up")[:2] == (1008, 1008); n += 1
    return n + _extra(m)


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
    n += ok(m.snap_size(1001, 1001, 8, 'up', 0.0) == (1008, 1008))
    n += ok(m.snap_size(1001, 1001, 8, 'up', 1.0)[0] * m.snap_size(1001, 1001, 8, 'up', 1.0)[1] <= 1_000_000)
    n += ok((lambda s: s[0] * s[1] <= 2_000_000 and s[0] % 64 == 0 and s[1] % 64 == 0)(m.snap_size(2000, 1500, 64, 'up', 2.0)))
    n += ok('too small' in rs(m.snap_size, 100, 100, 64, 'up', 0.001))
    n += ok(rs(m.snap_size, 100, 100, 8, 'up', -2) is not None)
    n += ok(m.snap_report(1000, 750, 8, 'nearest')[2].startswith('1000x750 -> 1000x752 (nearest, multiple of 8, '))
    n += ok(m.snap_report(100, 100, 64, 'up')[:2] == (128, 128))
    n += ok(m.snap_report(1024, 1024, 64, 'nearest')[2] == '1024x1024 already fits a multiple of 64, kept')
    n += ok('lowered to stay under 1 MP' in m.snap_report(1001, 1001, 8, 'up', 1.0)[2])
    n += ok('shape changed by' in m.snap_report(70, 100, 64, 'nearest')[2])
    n += ok(m.SYSizeSnap().run(1001, 1001, 8, 'up')[:2] == (1008, 1008))
    return n
