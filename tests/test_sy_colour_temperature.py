import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_colour_temperature as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def near(a, b, eps=1e-6):
    return abs(a - b) < eps


def run():
    n = 0
    assert m.temperature_gains(0, 0) == (1.0, 1.0, 1.0); n += 1
    g = m.temperature_gains(100, 0)
    assert near(g[0], 1.2) and near(g[1], 1.0) and near(g[2], 0.8); n += 1
    g = m.temperature_gains(-100, 0)
    assert near(g[0], 0.8) and near(g[2], 1.2); n += 1
    g = m.temperature_gains(50, 0)
    assert near(g[0], 1.1) and near(g[2], 0.9); n += 1
    g = m.temperature_gains(0, 100)
    assert near(g[1], 0.85) and g[0] == 1.0 and g[2] == 1.0; n += 1
    g = m.temperature_gains(0, -100)
    assert near(g[1], 1.15); n += 1
    g = m.temperature_gains(0, -40)
    assert near(g[1], 1.06); n += 1
    g = m.temperature_gains(30, 20)
    assert near(g[0], 1.06) and near(g[1], 0.97) and near(g[2], 0.94); n += 1
    assert m.apply_gains((0.5, 0.5, 0.5), (1, 1, 1)) == (0.5, 0.5, 0.5); n += 1
    assert m.apply_gains((0.95, 0.5, 0.5), (1.2, 1, 1))[0] == 1.0; n += 1
    assert m.apply_gains((0.5, 0.5, 0.0), (1, 1, 0.5))[2] == 0.0; n += 1
    msg = raises(m.temperature_gains, 101, 0)
    assert msg and "warmth" in msg; n += 1
    msg = raises(m.temperature_gains, 0, -101)
    assert msg and "tint" in msg; n += 1
    assert raises(m.temperature_gains, -100.5, 0); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYColourTemperature"] == "Colour Temperature SY"; n += 1
    return n
