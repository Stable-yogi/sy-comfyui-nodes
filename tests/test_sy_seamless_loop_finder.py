import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_seamless_loop_finder as m


def _raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    # frame values: a sawtooth wave with period 10 -> frame 3 and 13 and 23 look alike
    wave = [[(i % 10) / 10.0, 0.5] for i in range(30)]
    mat = m.distance_matrix(wave)
    assert len(mat) == 30 and mat[0][0] == 0 and mat[0][10] == 0 and mat[0][5] > 20
    assert abs(mat[0][5] - mat[5][0]) < 1e-9
    n += 3
    c = m.rank_loops(mat, 8, 0, 3)
    assert len(c) == 3 and c[0][0] == 0 and c[0][3] % 10 == 0 and c[0][2] - c[0][1] == c[0][3]
    assert all(c[i][0] <= c[i + 1][0] for i in range(2))
    n += 3
    c = m.rank_loops(mat, 8, 12, 5)
    assert all(8 <= x[3] <= 12 for x in c) and c[0][3] == 10
    n += 2
    # max_length 0 means the whole clip: longest loop is n-1
    c = m.rank_loops(mat, 29, 0, 1)
    assert c[0][1] == 0 and c[0][2] == 29
    n += 1
    # near copies are skipped
    c = m.rank_loops([[0.0] * 10 for _ in range(10)], 2, 0, 3)
    assert len(c) == 3 and len({(x[1], x[2]) for x in c}) == 3
    assert all(abs(a[1] - b[1]) > 1 or abs(a[2] - b[2]) > 1 for a in c for b in c if a is not b)
    n += 2
    # bad input
    assert _raises(m.rank_loops, [[0.0] * 5 for _ in range(5)], 2, 0, 1)      # fewer than 8 frames
    assert _raises(m.rank_loops, mat, 40, 0, 1)                                # min longer than clip
    assert _raises(m.rank_loops, mat, 10, 5, 1)                                # min above max
    assert _raises(m.rank_loops, mat, 1, 0, 1)
    assert _raises(m.rank_loops, mat, 8, 0, 0)
    assert _raises(m.rank_loops, mat[:-1], 8, 0, 1)                            # not square
    assert _raises(m.distance_matrix, [])
    assert _raises(m.distance_matrix, [[0.0], [0.0, 1.0]])
    n += 8
    rep = m.build_report(c, 10)
    assert "scaled 0..100" in rep and "lower is better" in rep and rep.count("\n") == 3
    n += 2
    assert m.SYSeamlessLoopFinder.RETURN_TYPES == ("IMAGE", "INT", "INT", "INT", "STRING")
    n += 1
    try:
        import torch
        frames = torch.zeros(30, 20, 40, 3)
        for i in range(30):
            frames[i] += (i % 10) / 10.0
        out, s, e, length, report = m.SYSeamlessLoopFinder().run(frames, 8, 0, 16, 2)
        assert out.shape[0] == length == e - s and length % 10 == 0 and "score" in report
        n += 2
        try:
            m.SYSeamlessLoopFinder().run(frames[:4], 2, 0, 16, 1)
            raise SystemExit("short clip must raise")
        except ValueError:
            n += 1
    except ImportError:
        pass
    return n
