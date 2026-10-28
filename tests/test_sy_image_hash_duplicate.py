import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_hash_duplicate as m


def ramp(w, h, flip=False, add=0.0, scale=1.0):
    """Brightness grows from left to right (or right to left when flip is true)."""
    return [[((w - 1 - x) if flip else x) * scale + add for x in range(w)] for _ in range(h)]


def bad(fn, *args):
    try:
        fn(*args)
    except ValueError as e:
        return str(e)
    raise SystemExit("must raise: %r" % (args,))


def run():
    a = ramp(16, 16)
    bits = m.average_hash(a, 8)
    assert len(bits) == 64
    assert bits == ([0] * 4 + [1] * 4) * 8                                   # dark left half, bright right half
    assert m.average_hash(ramp(64, 40), 8) == bits                           # same picture, other size
    assert m.average_hash(ramp(16, 16, add=50.0), 8) == bits                 # brighter overall: same fingerprint
    assert m.average_hash(ramp(16, 16, scale=2.0), 8) == bits                # more contrast: same fingerprint
    assert m.average_hash(ramp(16, 16, flip=True), 8) == ([1] * 4 + [0] * 4) * 8
    assert m.average_hash([[5.0] * 10] * 10, 8) == [0] * 64                  # flat picture
    assert len(m.average_hash([[1.0, 2.0]], 8)) == 64                        # smaller than the grid still works
    assert len(m.average_hash(ramp(100, 100), 16)) == 256
    assert m.hamming([0, 1, 1, 0], [0, 1, 1, 0]) == 0
    assert m.hamming([0, 1, 1, 0], [1, 0, 1, 0]) == 2
    assert m.hamming([0] * 64, [1] * 64) == 64
    assert "different lengths" in bad(m.hamming, [0, 1], [0])
    # comparing
    d, dup, rep = m.compare_grids(a, ramp(32, 32), 8, 5)
    assert d == 0 and dup is True and "near duplicate" in rep and "0 of 64" in rep
    d, dup, rep = m.compare_grids(a, ramp(16, 16, flip=True), 8, 5)
    assert d == 64 and dup is False and "different pictures" in rep
    # threshold boundary on an 8x8 grid (one cell per pixel): 32 dark cells and 32 bright cells
    base_grid = [[10.0 if (x + y * 8) < 32 else 20.0 for x in range(8)] for y in range(8)]

    def with_flips(k):
        g = [row[:] for row in base_grid]
        for i in range(k):                              # make k bright cells dark
            g[7 - i // 8][i % 8] = 10.0
        return g

    assert m.hamming(m.average_hash(base_grid, 8), m.average_hash(with_flips(5), 8)) == 5
    assert m.hamming(m.average_hash(base_grid, 8), m.average_hash(with_flips(6), 8)) == 6
    d, dup, _ = m.compare_grids(base_grid, with_flips(5), 8, 5)
    assert d == 5 and dup is True                       # distance equal to the limit counts as a duplicate
    d, dup, _ = m.compare_grids(base_grid, with_flips(6), 8, 5)
    assert d == 6 and dup is False                      # one more than the limit does not
    d, dup, _ = m.compare_grids(a, a, 8, 0)
    assert d == 0 and dup is True
    assert "threshold" in bad(m.compare_grids, a, a, 8, -1)
    assert "no pixels" in bad(m.average_hash, [], 8)
    assert "no pixels" in bad(m.average_hash, [[]], 8)
    assert "at least 2" in bad(m.average_hash, a, 1)
    assert m.SYImageHashDuplicate.RETURN_TYPES == ("INT", "BOOLEAN", "STRING")
    return 28
