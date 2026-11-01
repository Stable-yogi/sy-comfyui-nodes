import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_repeater as m


def run():
    n = 0
    obj = {"a": [1, 2]}
    out = m.fan_out(obj)
    assert isinstance(out, tuple) and len(out) == 8
    assert all(x is obj for x in out)
    n += 2
    assert all(x == 12345678 for x in m.fan_out(12345678, 3))
    assert len(m.fan_out(7, 1)) == 1 and len(m.fan_out(7, 16)) == 16
    n += 2
    for bad in (0, 17, -1, 2.5):
        try:
            m.fan_out(1, bad)
            raise SystemExit("bad count must raise")
        except ValueError:
            pass
        n += 1
    cls = m.SYRepeater
    assert len(cls.RETURN_TYPES) == 8 and cls.RETURN_NAMES[0] == "out_1" and cls.RETURN_NAMES[7] == "out_8"
    res = cls().run(obj)
    assert len(res) == 8 and all(x is obj for x in res)
    n += 2
    return n
