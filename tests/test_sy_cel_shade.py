import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_cel_shade as m
import _sy_ae_common as ae


def run():
    n = 0
    # normal: 3 levels give 0, 0.5, 1
    assert m.quantise_levels(0.0, 3) == 0.0
    assert m.quantise_levels(0.45, 3) == 0.5
    assert m.quantise_levels(1.0, 3) == 1.0
    n += 3
    # edge: 2 levels is black or white; out-of-range brightness is clamped
    assert m.quantise_levels(0.49, 2) == 0.0 and m.quantise_levels(0.51, 2) == 1.0
    assert m.quantise_levels(-1, 5) == 0.0 and m.quantise_levels(9, 5) == 1.0
    n += 2
    # result is always one of the allowed steps, and never decreases as the value rises
    steps = {i / 11.0 for i in range(12)}
    prev = 0.0
    for i in range(0, 101):
        q = m.quantise_levels(i / 100.0, 12)
        assert min(abs(q - s) for s in steps) < 1e-9 and q >= prev
        prev = q
    n += 1
    # ink strength: none for flat areas, full for hard edges
    assert m.edge_amount(0.0) == 0.0 and m.edge_amount(1.0) == 1.0
    assert 0.0 < m.edge_amount(0.1) < 1.0
    n += 2
    # refusals
    for bad in (1, 0):
        try:
            m.quantise_levels(0.5, bad)
            raise SystemExit("expected ValueError")
        except ValueError as e:
            assert "levels" in str(e)
    n += 2
    try:
        ae.check_shape((1, 4, 4, 2))
        raise SystemExit("expected ValueError")
    except ValueError:
        pass
    n += 1
    d = m.SYCelShade.INPUT_TYPES()["required"]
    assert d["levels"][1]["default"] == 5 and d["outline_width"][1]["max"] == 6
    n += 1
    return n
