import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_unit_convert as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    c = m.convert
    assert c(1, "length", "mi", "km", 6)[0] == 1.609344; n += 1
    assert c(100, "temperature", "c", "f", 4)[0] == 212.0; n += 1
    assert c(0, "temperature", "k", "c", 4)[0] == -273.15; n += 1
    assert c(1, "data size", "gb", "mb", 0)[0] == 1024.0; n += 1
    assert c(1, "length", "m", "ft") == (3.2808, "1 m = 3.2808 ft"); n += 1
    assert c(32, "temperature", "f", "c", 2)[0] == 0.0; n += 1
    assert c(0, "temperature", "c", "k", 2)[0] == 273.15; n += 1
    assert c(1, "weight", "lb", "oz", 3)[0] == 16.0; n += 1
    assert c(36, "speed", "km/h", "m/s", 3)[0] == 10.0; n += 1
    assert c(1, "speed", "kn", "km/h", 3)[0] == 1.852; n += 1
    assert c(2, "time", "h", "min", 0)[0] == 120.0; n += 1
    assert c(1500, "time", "ms", "s", 1)[0] == 1.5; n += 1
    assert c(1, "weight", "kg", "mg", 0)[0] == 1000000.0; n += 1
    # names: case and spaces
    assert c(1, "length", " KM ", "M", 0)[0] == 1000.0; n += 1
    # same unit, zero, negative, huge, tiny
    assert c(5, "length", "m", "m")[0] == 5.0; n += 1
    assert c(0, "length", "m", "ft")[0] == 0.0; n += 1
    assert c(-2, "length", "m", "cm", 0)[0] == -200.0; n += 1
    assert c(1e12, "data size", "tb", "b", 0)[0] == 1e12 * 1024.0 ** 4; n += 1
    assert c(0.00001, "length", "m", "km", 2)[1] == "0.00001 m = 0 km"; n += 1
    assert str(c(-0.00001, "length", "m", "km", 2)[0]) == "0.0"; n += 1
    assert c(1, "length", "m", "ft", 0)[1] == "1 m = 3 ft"; n += 1
    # round trip
    assert abs(c(c(7, "temperature", "c", "f", 12)[0], "temperature", "f", "c", 6)[0] - 7.0) < 1e-6; n += 1
    # refusals
    msg = _raises(c, 1, "length", "kg", "m")
    assert "not a unit of length" in msg and "mi" in msg; n += 1
    assert "not a unit of temperature" in _raises(c, 1, "temperature", "c", "m"); n += 1
    assert "quantity" in _raises(c, 1, "mass", "kg", "g"); n += 1
    assert "absolute zero" in _raises(c, -300, "temperature", "c", "f"); n += 1
    assert "precision" in _raises(c, 1, "length", "m", "ft", 13); n += 1
    assert "normal number" in _raises(c, float("nan"), "length", "m", "ft"); n += 1
    assert "normal number" in _raises(c, float("inf"), "length", "m", "ft"); n += 1
    assert m.units_of("time") == ("ms", "s", "min", "h", "d"); n += 1
    node = m.SYUnitConvert()
    assert node.run(1.0, "length", "m", "ft", 4) == (3.2808, "1 m = 3.2808 ft"); n += 1
    return n
