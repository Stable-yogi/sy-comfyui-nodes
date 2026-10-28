import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_longest_side_scale as m


def _raises(*args):
    try:
        m.scale_longest_side(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.scale_longest_side(2000, 1000, 1000, 1) == (1000, 500); n += 1
    assert m.scale_longest_side(1000, 2000, 1000, 1) == (500, 1000); n += 1
    assert m.scale_longest_side(1000, 1000, 512, 8) == (512, 512); n += 1
    assert m.scale_longest_side(1920, 1080, 1024, 8) == (1024, 576); n += 1
    assert m.scale_longest_side(1000, 1000, 1000, 64) == (1024, 1024); n += 1  # non-multiple rounds
    assert m.scale_longest_side(100, 1, 1000, 8) == (1000, 8); n += 1  # extreme aspect keeps one multiple
    assert m.scale_longest_side(1, 1, 1, 1) == (1, 1); n += 1
    assert m.scale_longest_side(10, 10, 65536, 1) == (65536, 65536); n += 1  # huge but legal
    for bad in ((0, 5, 100, 1), (5, 0, 100, 1), (5, 5, 0, 1), (5, 5, 70000, 1), (5, 5, 100, 0), (-1, 5, 100, 1)):
        assert _raises(*bad), bad
        n += 1
    assert m.SYLongestSideScale().run(2000, 1000, 1000, 1) == (1000, 500); n += 1
    return n
