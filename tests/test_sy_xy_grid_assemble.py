import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_xy_grid_assemble as m


def run():
    n = 0
    m.check_count(6, 3, 2); n += 1
    for args in ((5, 3, 2), (7, 3, 2), (0, 1, 1)):
        try:
            m.check_count(*args)
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    assert m.SYXYGridAssemble.RETURN_TYPES == ("IMAGE",); n += 1
    return n
