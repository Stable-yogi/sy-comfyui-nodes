import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_batch_pick as m


def run():
    assert m.pick_indices(5, 0, 1) == [0]
    assert m.pick_indices(5, 2, 3) == [2, 3, 4]
    assert m.pick_indices(5, 3, 4) == [3, 4, 0, 1]
    assert m.pick_indices(5, 7, 2) == [2, 3]
    assert m.pick_indices(1, 9, 3) == [0, 0, 0]
    assert len(m.pick_indices(4, 0, 64)) == 64
    for bad in ((0, 0, 1), (3, 0, 0)):
        try:
            m.pick_indices(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            pass
    assert m.SYBatchPick.RETURN_TYPES == ("IMAGE", "STRING")
    # wrap off: no wrap-around, plain message instead
    assert m.pick_indices(5, 1, 3, False) == [1, 2, 3]
    assert m.pick_indices(5, 0, 5, False) == [0, 1, 2, 3, 4]
    try:
        m.pick_indices(5, 3, 3, False)
        raise SystemExit("expected ValueError")
    except ValueError as e:
        assert "only holds 5" in str(e)
    assert m.pick_indices(5, 3, 3) == [3, 4, 0]   # default still wraps
    assert m.pick_info(6, [3, 4]) == "Took 3, 4 of 6 (counting from 0)"
    assert list(m.SYBatchPick.INPUT_TYPES()["optional"]) == ["wrap"]
    return 9 + 9  # checks
