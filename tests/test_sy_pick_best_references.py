import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_pick_best_references as m

LABELS = "face close-up\nleft profile\nfull body front\nback view\nhands"


def run():
    n = 0
    picks, names, notes = m.pick_references(LABELS, "face\nfull body\nback", 5)
    assert picks == [0, 2, 3] and names == ["face close-up", "full body front", "back view"] and notes == [], (picks, notes); n += 1
    picks, names, notes = m.pick_references(LABELS, "5, 1", 5)
    assert picks == [4, 0, 1] and names[2] == "left profile", picks; n += 1
    picks, _, notes = m.pick_references(LABELS, "feet\nface", 5)
    assert picks == [0, 1, 2] and "feet" in notes[0], (picks, notes); n += 1
    picks, names, notes = m.pick_references("", "", 2)
    assert picks == [0, 1, 1] and names == ["shot 1", "shot 2", "shot 2"] and "repeats" in notes[0], (picks, notes); n += 1
    picks, names, notes = m.pick_references("face", "face", 2)
    assert names[1] == "shot 2" and "1 labels for 2 stills" in notes[0], notes; n += 1
    for bad in ((LABELS, "face", 0), (LABELS, "9", 5), (LABELS, "a\nb\nc\nd", 5)):
        try:
            m.pick_references(*bad)
            raise SystemExit("bad input must raise: %r" % (bad,))
        except ValueError:
            n += 1
    line = m.prompt_line(["face close-up", "full body front", "back view"], "the young woman")
    assert line.startswith("Picture 1 shows the young woman (face close-up); Picture 2") and line.endswith("every shot."), line; n += 1
    try:
        import torch
    except ImportError:
        return n
    imgs = torch.stack([torch.full((4, 4, 3), i / 10.0) for i in range(5)])
    p1, p2, p3, line, info = m.SYPickBestReferences().run(imgs, "back\nface", LABELS, "Mia")
    assert tuple(p1.shape) == (1, 4, 4, 3) and abs(float(p1[0, 0, 0, 0]) - 0.3) < 1e-6 and abs(float(p2[0, 0, 0, 0])) < 1e-6, info; n += 1
    assert abs(float(p3[0, 0, 0, 0]) - 0.1) < 1e-6 and info.startswith("Picture 1 = still 4, Picture 2 = still 1, Picture 3 = still 2"), info; n += 1
    return n
