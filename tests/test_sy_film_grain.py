import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_film_grain as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-6):
    return abs(a - b) < eps


def run():
    n = 0
    assert m.grain_grid_size(100, 200, 1) == (100, 200); n += 1
    assert m.grain_grid_size(100, 200, 3) == (34, 67); n += 1
    assert m.grain_grid_size(1, 1, 32) == (1, 1); n += 1
    assert m.seeded_noise(5, 10) == m.seeded_noise(5, 10); n += 1
    assert m.seeded_noise(5, 10) != m.seeded_noise(6, 10); n += 1
    assert len(m.seeded_noise(1, 7)) == 7; n += 1
    big = m.seeded_noise(3, 5000)
    assert abs(sum(big) / len(big)) < 0.1; n += 1
    assert near(m.add_grain_value(0.5, 1.0, 0.1), 0.6); n += 1
    assert m.add_grain_value(0.95, 1.0, 0.2) == 1.0; n += 1
    assert m.add_grain_value(0.05, -1.0, 0.2) == 0.0; n += 1
    assert m.add_grain_value(0.5, 3.0, 0.0) == 0.5; n += 1
    assert raises(m.grain_grid_size, 10, 10, 0); n += 1
    assert m.grain_weight(0.5, "even") == 1.0 and m.grain_weight(0.0, "even") == 1.0; n += 1
    assert near(m.grain_weight(0.5, "midtones"), 1.0) and m.grain_weight(0.0, "midtones") == 0.0 and m.grain_weight(1.0, "midtones") == 0.0; n += 1
    assert near(m.grain_weight(0.25, "midtones"), 0.75) and m.grain_weight(2.0, "midtones") == 0.0; n += 1
    assert raises(m.grain_weight, 0.5, "heavy"); n += 1
    assert "no grain" in m.grain_info(0, 1, 0, False, "even", True, 1, 64, 64); n += 1
    t = m.grain_info(0.1, 2, 7, True, "midtones", False, 4, 512, 256, "note")
    assert "colour grain" in t and "size 2 px" in t and "seed 7" in t and "the same grain on all 4 frames" in t and "512x256" in t and "note" in t; n += 1
    assert "different grain on all 3 frames" in m.grain_info(0.1, 1, 1, False, "even", True, 3, 8, 8); n += 1
    assert "frames" not in m.grain_info(0.1, 1, 1, False, "even", True, 1, 8, 8); n += 1
    assert m.SYFilmGrain.RETURN_NAMES == ("image", "info"); n += 1
    return n
