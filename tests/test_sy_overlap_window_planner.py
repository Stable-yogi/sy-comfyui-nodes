import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_overlap_window_planner as m

FULL = "shift back so it is full"
SHORT = "keep it short"


def run():
    n = 0
    w = m.plan_windows(200, 56, 5, FULL)
    assert w == [(0, 56), (51, 107), (102, 158), (144, 200)]; n += 1
    assert m.plan_windows(200, 56, 5, SHORT)[-1] == (153, 200); n += 1
    assert all(e - s == 56 for s, e in w); n += 1
    assert m.plan_windows(200, 56, 5, SHORT)[:3] == w[:3]; n += 1
    # exact fit: no extra window
    assert m.plan_windows(107, 56, 5, FULL) == [(0, 56), (51, 107)]; n += 1
    # edge: one window
    assert m.plan_windows(56, 56, 5) == [(0, 56)]; n += 1
    assert m.plan_windows(10, 56, 5) == [(0, 10)]; n += 1
    assert m.plan_windows(1, 2, 0) == [(0, 1)]; n += 1
    # edge: overlap 0
    assert m.plan_windows(100, 50, 0) == [(0, 50), (50, 100)]; n += 1
    # edge: biggest numbers
    big = m.plan_windows(100000, 10000, 5000, FULL)
    assert big[0] == (0, 10000) and big[-1][1] == 100000 and len(big) == 19; n += 3
    # no empty window, none starting at or beyond total
    for mode in (FULL, SHORT):
        for total in range(1, 60):
            for win in (2, 5, 9):
                for ov in range(0, win):
                    ws = m.plan_windows(total, win, ov, mode)
                    assert ws[0][0] == 0 and ws[-1][1] == total
                    assert all(s < e and s < total for s, e in ws)
                    for a, b in zip(ws, ws[1:]):
                        assert b[0] > a[0] and b[0] <= a[1]
    n += 1
    assert m.plan_text([(0, 56), (51, 107)]) == "1: 0-55 (56 frames)\n2: 51-106 (56 frames)"; n += 1
    assert m.pick_window(w, 0) == (0, 0, 0); n += 1
    assert m.pick_window(w, 4) == (144, 200, 56); n += 1
    out = m.SYOverlapWindowPlanner().run(200, 56, 5, FULL, 2)
    assert out[1] == 4 and out[2:] == (51, 107, 56) and out[0].startswith("1: 0-55"); n += 3
    # refusals
    for args, word in (((200, 10, 10, FULL), "overlap must be smaller than the window"),
                       ((200, 10, 12, FULL), "overlap must be smaller than the window"),
                       ((200, 10, 2, "nope"), "last_window")):
        try:
            m.plan_windows(*args)
            raise SystemExit("must raise")
        except ValueError as e:
            assert word in str(e)
    n += 3
    try:
        m.pick_window(w, 5)
        raise SystemExit("must raise")
    except ValueError as e:
        assert "only 4 windows" in str(e)
    n += 1
    assert m.SYOverlapWindowPlanner.RETURN_TYPES == ("STRING", "INT", "INT", "INT", "INT"); n += 1
    return n
