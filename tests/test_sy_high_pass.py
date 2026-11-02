import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_high_pass as m


def refuses(fn, *args):
    try:
        fn(*args)
    except ValueError as e:
        return len(str(e)) > 10
    return False


def run():
    n = 0
    assert m.high_pass_value(0.5, 0.5, 1.0) == 0.5; n += 1
    assert abs(m.high_pass_value(0.6, 0.4, 1.0) - 0.7) < 1e-9; n += 1
    assert m.high_pass_value(0.9, 0.1, 4.0) == 1.0; n += 1
    assert m.high_pass_value(0.1, 0.9, 4.0) == 0.0; n += 1
    assert m.high_pass_value(0.9, 0.1, 0.0) == 0.5; n += 1
    assert m.added_value(0.7, 0.2, 0.0) == 0.7; n += 1
    assert abs(m.added_value(0.6, 0.4, 1.0) - 0.8) < 1e-9; n += 1
    assert m.added_value(0.9, 0.1, 4.0) == 1.0; n += 1
    k = m.gaussian_kernel(1)
    assert abs(sum(k) - 1.0) < 1e-9 and len(k) % 2 == 1 and k[len(k) // 2] == max(k); n += 1
    k = m.gaussian_kernel(100)
    assert abs(sum(k) - 1.0) < 1e-9 and len(k) == 2 * 150 + 1; n += 1
    assert refuses(m.gaussian_kernel, 0); n += 1
    assert m.check_settings(1, 0, "grey detail") is None; n += 1
    assert m.check_settings(100, 4, "added to original") is None; n += 1
    assert refuses(m.check_settings, 0, 1, "grey detail"); n += 1
    assert refuses(m.check_settings, 101, 1, "grey detail"); n += 1
    assert refuses(m.check_settings, 6, 5, "grey detail"); n += 1
    assert refuses(m.check_settings, 6, 1, "sharp"); n += 1
    assert m.SYHighPass.CATEGORY == "SY/Image"; n += 1
    return n
