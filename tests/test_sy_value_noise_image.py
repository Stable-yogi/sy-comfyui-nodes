import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_value_noise_image as m


def _raises(fn, *args, word=""):
    try:
        fn(*args)
    except ValueError as e:
        return word in str(e)
    return False


def run():
    n = 0
    g = m.noise_grid(24, 16, 8, 3, 7)
    assert len(g) == 16 and len(g[0]) == 24; n += 1
    flat = [v for row in g for v in row]
    assert min(flat) >= 0.0 and max(flat) <= 1.0; n += 1
    assert max(flat) - min(flat) > 0.1; n += 1                       # not flat
    assert m.noise_grid(24, 16, 8, 3, 7) == g; n += 1                # same seed, same picture
    assert m.noise_grid(24, 16, 8, 3, 8) != g; n += 1                # other seed differs
    assert m.noise_grid(24, 16, 8, 1, 7) != g; n += 1                # octaves change the picture
    small = m.noise_grid(1, 1, 256, 6, 0)                            # smallest picture, biggest scale, most octaves
    assert len(small) == 1 and 0.0 <= small[0][0] <= 1.0; n += 1
    # neighbouring pixels differ little when the scale is large (smooth)
    s = m.noise_grid(32, 1, 64, 1, 3)[0]
    assert max(abs(s[i + 1] - s[i]) for i in range(31)) < 0.1; n += 1
    assert 0.0 <= m.lattice_value(-3, 5, m.seed_term(-4, 2)) <= 1.0; n += 1
    assert m.lattice_value(1, 2, 3) == m.lattice_value(1, 2, 3); n += 1
    assert _raises(m.noise_grid, 0, 4, 8, 2, 0, word="width"); n += 1
    assert _raises(m.noise_grid, 4, 4, 0.5, 2, 0, word="scale"); n += 1
    assert _raises(m.noise_grid, 4, 4, 8, 0, 0, word="octaves"); n += 1
    assert _raises(m.check_args, 4, 4, 8, 2, 0, word="batch"); n += 1
    assert m.SYValueNoiseImage.RETURN_TYPES == ("IMAGE", "MASK"); n += 1
    return n
