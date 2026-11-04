import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_best_frames_per_shot as m


def run():
    n = 0
    starts, notes = m.parse_starts("30, 10,30\n50", 40)
    assert starts == [0, 10, 30] and notes == ["shot start 50 is past the last frame (39), left out"], (starts, notes); n += 1
    assert m.parse_starts("", 5) == ([0], []); n += 1
    for bad in (("a,b", 10), ("-1", 10), ("0", 0)):
        try:
            m.parse_starts(*bad)
            raise SystemExit("bad input must raise")
        except ValueError:
            n += 1

    assert m.merge_short([0, 80, 82, 89, 108, 136, 147], 24) == [0, 80, 108, 136], m.merge_short([0, 80, 82, 89, 108, 136, 147], 24); n += 1
    assert m.merge_short([0, 1, 2], 0) == [0, 1, 2] and m.merge_short([0, 1, 2], 1) == [0, 1, 2]; n += 1
    try:
        m.merge_short([0], -1)
        raise SystemExit("negative min_shot must raise")
    except ValueError:
        n += 1
    r = m.shot_ranges([0, 10, 30], 40, 2)
    assert r == [(2, 7), (12, 27), (32, 37)], r; n += 1
    r = m.shot_ranges([0, 3], 5, 2)
    assert r == [(1, 1), (3, 3)], r; n += 1
    try:
        m.shot_ranges([0], 5, -1)
        raise SystemExit("negative edge must raise")
    except ValueError:
        n += 1

    scores = [0.0] * 40
    scores[5] = 9.0
    scores[4] = 9.0
    scores[20] = 5.0
    scores[33] = 1.0
    picks = m.pick_frames([(2, 7), (12, 27), (32, 37)], 1, "sharpest", scores)
    assert picks == [(0, 4), (1, 20), (2, 33)], picks; n += 1
    picks = m.pick_frames([(2, 7)], 2, "sharpest", scores)
    assert picks == [(0, 4), (0, 5)], picks; n += 1
    picks = m.pick_frames([(0, 10), (20, 20)], 3, "middle")
    assert picks == [(0, 2), (0, 5), (0, 8), (1, 20)], picks; n += 1
    for bad in (([(0, 1)], 0, "middle", None), ([(0, 1)], 1, "best", None), ([(0, 1)], 1, "sharpest", None)):
        try:
            m.pick_frames(*bad)
            raise SystemExit("bad input must raise")
        except ValueError:
            n += 1

    kept, notes = m.apply_drop([(0, 4), (1, 20), (2, 33)], "2, 9")
    assert kept == [(0, 4), (2, 33)] and notes == ["drop 9: there are only 3 pictures"], (kept, notes); n += 1
    for bad in ("x", "0", "1,2"):
        try:
            m.apply_drop([(0, 4), (1, 5)], bad)
            raise SystemExit("bad drop must raise: %r" % bad)
        except ValueError:
            n += 1
    assert m.labels_for([(0, 4), (2, 33)], "face\nback\nfeet") == "face\nfeet"; n += 1
    assert m.labels_for([(0, 4), (3, 50)], "face") == "face\nshot 4"; n += 1

    try:
        import torch
    except ImportError:
        return n
    imgs = torch.zeros(12, 8, 8, 3)
    imgs[4, ::2, ::2, :] = 1.0   # shot 1 sharp frame
    imgs[9, ::2, :, :] = 1.0     # shot 2 sharp frame
    out, labels, picked, count, info = m.SYBestFramesPerShot().run(imgs, "6", 1, "sharpest", 1, "front\nback", "")
    assert picked == "4,9" and count == 2 and labels == "front\nback" and tuple(out.shape) == (2, 8, 8, 3), (picked, labels); n += 1
    assert info.startswith("2 shots, 2 pictures kept"); n += 1
    out, _, picked, count, _ = m.SYBestFramesPerShot().run(imgs, "6", 1, "middle", 0, "", "1")
    assert picked == "8" and count == 1, picked; n += 1
    _, _, picked, count, info = m.SYBestFramesPerShot().run(imgs, "6", 1, "middle", 0, "", "", 8)
    assert picked == "6" and count == 1 and "1 short shots joined" in info, (picked, info); n += 1
    return n
