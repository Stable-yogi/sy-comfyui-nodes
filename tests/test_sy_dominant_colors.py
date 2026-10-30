import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_dominant_colors as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def near3(a, b, eps=1e-6):
    return all(abs(x - y) < eps for x, y in zip(a, b))


RED, GREEN, BLUE = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)
BLACK, WHITE = (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)


def run():
    n = 0
    two = [BLACK] * 30 + [WHITE] * 70
    r = m.kmeans_clusters(two, 2)
    assert near3(r[0][0], WHITE) and r[0][1] == 70; n += 1
    assert near3(r[1][0], BLACK) and r[1][1] == 30; n += 1
    three = [RED] * 50 + [GREEN] * 30 + [BLUE] * 20
    c = m.kmeans_colours(three, 3)
    assert near3(c[0], RED) and near3(c[1], GREEN) and near3(c[2], BLUE); n += 1
    assert [s for _, s in m.kmeans_clusters(three, 3)] == [50, 30, 20]; n += 1
    # deterministic: same answer twice, whatever the pixel order
    assert m.kmeans_colours(three, 3) == m.kmeans_colours(list(reversed(three)), 3); n += 1
    # exactly `count` entries, even when there are fewer distinct colours
    one = [RED] * 10
    assert len(m.kmeans_colours(one, 4)) == 4; n += 1
    assert all(near3(c, RED) for c in m.kmeans_colours(one, 4)); n += 1
    assert len(m.kmeans_colours([BLUE], 12)) == 12; n += 1
    assert near3(m.kmeans_colours(three, 1)[0], tuple((50 * a + 30 * b + 20 * c2) / 100.0 for a, b, c2 in zip(RED, GREEN, BLUE))); n += 1
    # tie in size: darker first
    tie = [BLACK] * 5 + [WHITE] * 5
    assert near3(m.kmeans_colours(tie, 2)[0], BLACK); n += 1
    # rounds=0 still works (centres stay the quantile pixels)
    assert len(m.kmeans_colours(two, 2, rounds=0)) == 2; n += 1
    # sample size maths
    assert m.sample_dims(1000, 500, 128) == (128, 64); n += 1
    assert m.sample_dims(50, 40, 128) == (50, 40); n += 1
    assert m.sample_dims(4000, 1, 128) == (128, 1); n += 1
    assert m.sample_dims(1, 1, 16) == (1, 1); n += 1
    assert m.sample_index(0, 128, 1000) == 3 and m.sample_index(127, 128, 1000) == 996; n += 1
    # bad input
    assert raises(m.kmeans_colours, [], 3); n += 1
    assert raises(m.kmeans_colours, two, 0); n += 1
    assert raises(m.check_settings, 0, 128); n += 1
    assert raises(m.check_settings, 13, 128); n += 1
    assert raises(m.check_settings, 5, 8); n += 1
    assert raises(m.check_settings, 5, 600); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYDominantColors"] == "Dominant Colors SY"; n += 1
    return n
