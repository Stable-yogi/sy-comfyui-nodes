import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_noise_texture as m


def _raises(fn, *args, word=""):
    try:
        fn(*args)
    except ValueError as e:
        return word in str(e)
    return False


def run():
    n = 0
    # fixed values: integer maths only, so they must be identical everywhere
    assert abs(m.lattice_hash(0, 0, 0) - 0.4562260777354767) < 1e-12; n += 1
    assert abs(m.lattice_hash(1, 0, 0) - 0.2103562437022003) < 1e-12; n += 1
    assert abs(m.lattice_hash(0, 1, 0) - 0.6343207425983438) < 1e-12; n += 1
    assert abs(m.lattice_hash(5, 7, 123) - 0.23977245489130086) < 1e-12; n += 1
    assert abs(m.lattice_hash(100, 200, 2 ** 53) - 0.4152962212486417) < 1e-12; n += 1
    assert m.lattice_hash(3, 4, 9) == m.lattice_hash(3, 4, 9); n += 1      # repeatable
    assert m.lattice_hash(3, 4, 9) != m.lattice_hash(3, 4, 10); n += 1     # seed matters
    assert m.lattice_hash(3, 4, 9) != m.lattice_hash(4, 3, 9); n += 1      # x and y are not swappable
    vals = [m.lattice_hash(x, y, 7) for x in range(30) for y in range(30)]
    assert all(0.0 <= v <= 1.0 for v in vals); n += 1
    assert 0.4 < sum(vals) / len(vals) < 0.6; n += 1                       # spread around the middle
    assert m.smoothstep(0.0) == 0.0 and m.smoothstep(1.0) == 1.0 and m.smoothstep(0.5) == 0.5; n += 1
    assert m.octave_cell(64, 0) == 64 and m.octave_cell(64, 2) == 16; n += 1
    assert m.octave_cell(2, 5) == 1.0; n += 1                              # never below one pixel
    assert m.shape_value(0.5, 3.0) == 0.5; n += 1
    assert m.shape_value(0.9, 4.0) == 1.0 and m.shape_value(0.1, 4.0) == 0.0; n += 1
    assert abs(m.noise_at(10, 20, 64, 3, 5) - 0.4282044831141315) < 1e-12; n += 1
    assert m.noise_at(10, 20, 64, 3, 5) == m.noise_at(10, 20, 64, 3, 5); n += 1   # same seed, same mask
    assert m.noise_at(10, 20, 64, 3, 5) != m.noise_at(10, 20, 64, 3, 6); n += 1
    near = abs(m.noise_at(100, 100, 64, 1, 1) - m.noise_at(101, 100, 64, 1, 1))
    assert near < 0.05; n += 1                                             # smooth: neighbours are close
    assert all(0.0 <= m.noise_at(x, 3, 8, 6, 2) <= 1.0 for x in range(40)); n += 1
    assert _raises(m.check_args, 4, 64, 64.0, 3, 1.5, 0, -1.0, word="width"); n += 1
    assert _raises(m.check_args, 64, 64, 1.0, 3, 1.5, 0, -1.0, word="scale"); n += 1
    assert _raises(m.check_args, 64, 64, 64.0, 7, 1.5, 0, -1.0, word="octaves"); n += 1
    assert _raises(m.check_args, 64, 64, 64.0, 3, 0.0, 0, -1.0, word="contrast"); n += 1
    assert _raises(m.check_args, 64, 64, 64.0, 3, 1.5, -1, -1.0, word="seed"); n += 1
    assert _raises(m.check_args, 64, 64, 64.0, 3, 1.5, 0, 2.0, word="threshold"); n += 1
    assert m.SYMaskNoiseTexture.RETURN_TYPES == ("MASK",); n += 1
    return n
