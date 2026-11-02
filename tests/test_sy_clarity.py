import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_clarity as m
import _sy_ae_common as ae


def run():
    n = 0
    # normal: strongest in mid grey, weak at the ends
    assert m.midtone_weight(0.5) == 1.0
    assert m.midtone_weight(0.1) < m.midtone_weight(0.4)
    assert m.midtone_weight(0.9) < m.midtone_weight(0.6)
    n += 3
    # edge: pure black and pure white get nothing
    assert m.midtone_weight(0.0) == 0.0 and m.midtone_weight(1.0) == 0.0
    n += 1
    # symmetric
    assert abs(m.midtone_weight(0.2) - m.midtone_weight(0.8)) < 1e-12
    n += 1
    # blur weights add up to 1 and are symmetric
    w = ae.gaussian_weights(10.0)
    assert abs(sum(w) - 1.0) < 1e-9 and abs(w[0] - w[-1]) < 1e-12 and len(w) % 2 == 1
    n += 2
    # refusals
    for bad in (-0.1, 1.2):
        try:
            m.midtone_weight(bad)
            raise SystemExit("expected ValueError")
        except ValueError as e:
            assert "luma" in str(e)
    n += 2
    try:
        ae.gaussian_weights(0)
        raise SystemExit("expected ValueError")
    except ValueError:
        pass
    try:
        ae.check_shape((1, 0, 5, 3))
        raise SystemExit("expected ValueError")
    except ValueError as e:
        assert "no pixels" in str(e)
    n += 2
    d = m.SYClarity.INPUT_TYPES()["required"]
    assert d["radius"][1]["default"] == 20 and d["amount"][1]["default"] == 0.5
    n += 1
    return n
