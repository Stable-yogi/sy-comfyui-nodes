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
    assert m.SYSwapWidthHeight().run(10, 20, 1)[:2] == (20, 10); n += 1  # a truthy value from the UI is fine
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
    n += ok(m.swap_size(768, 1024, False, 'landscape') == (1024, 768))
    n += ok(m.swap_size(1024, 768, True, 'landscape') == (1024, 768))
    n += ok(m.swap_size(1024, 768, False, 'portrait') == (768, 1024))
    n += ok(m.swap_size(512, 512, True, 'portrait') == (512, 512))
    n += ok(m.swap_size(10, 20, True, 'use_swap_switch') == m.swap_size(10, 20, True))
    n += ok('force must be' in rs(m.swap_size, 10, 20, True, 'tall'))
    n += ok(m.swap_report(1024, 768, True)[2] == '1024x768 -> 768x1024 (swapped)')
    n += ok(m.swap_report(1024, 768, False)[2] == '1024x768 kept')
    n += ok(m.swap_report(1024, 768, False, 'landscape')[2] == '1024x768 already landscape, kept')
    n += ok(m.swap_report(768, 1024, False, 'landscape')[2] == '768x1024 -> 1024x768 (swapped to make it landscape)')
    n += ok(m.SYSwapWidthHeight().run(768, 1024, False, 'landscape')[:2] == (1024, 768))
    return n
