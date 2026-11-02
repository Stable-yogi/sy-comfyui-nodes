import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_echo_trail as m


def run():
    n = 0
    w = m.echo_weights(4, 0.6)
    assert len(w) == 4 and abs(sum(w) - 1) < 1e-9 and w[0] > w[1] > w[2] > w[3]; n += 1
    assert abs(w[1] / w[0] - 0.6) < 1e-9; n += 1
    assert m.echo_weights(1, 0.6) == [1.0]; n += 1
    assert m.echo_weights(3, 0.0) == [1.0, 0.0, 0.0]; n += 1
    w = m.echo_weights(12, 1.0)
    assert len(w) == 12 and abs(w[0] - 1 / 12) < 1e-9 and abs(sum(w) - 1) < 1e-9; n += 1
    for bad, text in (((0, 0.5), "between 1 and 12"), ((13, 0.5), "between 1 and 12"),
                      ((4, -0.1), "between 0 and 1"), ((4, 1.5), "between 0 and 1")):
        try:
            m.echo_weights(*bad)
            raise SystemExit("bad args must raise")
        except ValueError as e:
            assert text in str(e)
        n += 1
    assert m.source_index(0, 3) == 0 and m.source_index(5, 2) == 3; n += 2
    assert m.SYEchoTrail.RETURN_TYPES == ("IMAGE",); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYEchoTrail"] == "Echo Trail SY"; n += 1
    return n
