import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_number_format as m


def raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def run():
    n = 0
    f = m.format_number
    assert f(7) == "7"; n += 1
    assert f(7, pad_width=3) == "007"; n += 1
    assert f(3.14159, decimals=2) == "3.14"; n += 1
    assert f(3.14159, decimals=2, pad_width=4) == "0003.14"; n += 1
    assert f(-7, pad_width=3) == "-007"; n += 1
    assert f(5, prefix="v", suffix="px") == "v5px"; n += 1
    assert f(1234567, thousands=True) == "1,234,567"; n += 1
    assert f(1234.5, decimals=1, thousands=True) == "1,234.5"; n += 1
    assert f(7, pad_width=3, thousands=True) == "007"; n += 1
    assert f("12.5", decimals=0) in ("12", "13"); n += 1
    assert f(-0.001, decimals=1) == "0.0"; n += 1
    assert f(2.5, decimals=3) == "2.500"; n += 1
    assert raises(lambda: f(float("nan"))); n += 1
    assert raises(lambda: f(float("inf"))); n += 1
    assert raises(lambda: f("abc")); n += 1
    assert raises(lambda: f(None)); n += 1
    assert raises(lambda: f(1, decimals=11)); n += 1
    assert raises(lambda: f(1, pad_width=33)); n += 1
    node = m.SYTextNumberFormat()
    assert node.run(1.0, 0, 3) == ("001",); n += 1
    assert node.run(1.0, 0, 3, number_in=42) == ("042",); n += 1
    return n
