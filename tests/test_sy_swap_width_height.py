import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_swap_width_height as m


def _raises(*args):
    try:
        m.swap_size(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.swap_size(1024, 768, True) == (768, 1024); n += 1
    assert m.swap_size(1024, 768, False) == (1024, 768); n += 1
    assert m.swap_size(512, 512, True) == (512, 512); n += 1
    assert m.swap_size(0, 0, True) == (0, 0); n += 1
    assert m.swap_size(1, 65536, True) == (65536, 1); n += 1
    assert m.swap_size(1000003, 7, True) == (7, 1000003); n += 1  # huge, non-multiple
    for bad in ((-1, 5, True), (5, -1, False), (5, 5, "yes"), (5, 5, 1)):
        assert _raises(*bad), bad
        n += 1
    assert m.SYSwapWidthHeight().run(10, 20, 1) == (20, 10); n += 1  # a truthy value from the UI is fine
    return n
