import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_sketch_lines as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def run():
    n = 0
    for s in (0.5, 1.0, 2.5):
        k = m.gaussian_kernel(s)
        assert abs(sum(k) - 1.0) < 1e-9
        assert len(k) % 2 == 1
        assert all(abs(k[i] - k[-1 - i]) < 1e-12 for i in range(len(k)))
        n += 3
    assert _raises(m.gaussian_kernel, 0)
    n += 1
    assert m.xdog_value(0.9, 0.9, 20, 0.5, 30) == 1.0      # flat area is paper
    assert m.xdog_value(0.1, 0.9, 20, 0.5, 30) < 1e-6      # strong dark edge is line
    n += 2
    vals = [m.xdog_value(0.5, 0.5 + t / 100.0, 5, 0.4, 10) for t in range(0, 30)]
    assert all(vals[i] >= vals[i + 1] for i in range(len(vals) - 1))   # monotonic as b grows (d falls)
    assert all(0.0 <= v <= 1.0 for v in vals)
    n += 2
    assert _raises(m.xdog_value, 0.5, 0.5, 0.5, 0.5, 30)    # sharpness too low
    assert _raises(m.xdog_value, 0.5, 0.5, 20, 1.5, 30)     # cutoff too high
    assert _raises(m.xdog_value, 0.5, 0.5, 20, 0.5, 0.5)    # softness too low
    assert _raises(m.check_params, 0.1, 20, 0.5, 30)        # detail too low
    assert _raises(m.check_params, 5.0, 20, 0.5, 30)        # detail too high
    n += 5
    spec = m.SYSketchLines.INPUT_TYPES()["required"]
    assert list(spec) == ["image", "detail", "sharpness", "cutoff", "softness", "invert"]
    assert m.SYSketchLines.RETURN_TYPES == ("IMAGE",)
    n += 2
    return n
