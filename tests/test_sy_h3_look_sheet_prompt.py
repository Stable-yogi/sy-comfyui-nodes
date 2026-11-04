import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_look_sheet_prompt as m


def run():
    n = 0
    total, starts, windows = m.shot_plan(12, 10.0, 24)
    assert total == 241 and len(starts) == 12 and starts[0] == 0 and starts[1] == 20 and starts[-1] == 221, (total, starts); n += 1
    assert windows[0] == (0.0, 0.8) and windows[-1] == (9.2, 10.0), windows; n += 1
    total, starts, _ = m.shot_plan(1, 5.0, 24)
    assert total == 121 and starts == [0]; n += 1

    p, ss, labels, count, notes = m.build_look_sheet("the woman from Picture 1", "grey wall", "face set (6)", "", 6.0, 24, "calm")
    assert count == 6 and ss == "0,24,48,72,97,121" and labels.splitlines()[0] == "face front close-up", (ss, labels); n += 1
    assert p.startswith("A look sheet video of the woman from Picture 1. Setting: grey wall. Expression: calm. The camera is locked off"), p; n += 1
    assert "\n0.0-1.0s: hard cut, close-up of the face, front view, looking into the lens." in p, p; n += 1
    assert p.count("hard cut,") == 6 and notes == "", notes; n += 1

    _, _, _, count, notes = m.build_look_sheet("her", "", "full set (12)", "", 6.0, 24)
    assert count == 12 and "may merge" in notes, notes; n += 1

    p, _, labels, count, notes = m.build_look_sheet("him", "", "custom", "full body back\nslow spin on the spot\nbird's eye view", 6.0, 24)
    assert count == 3 and "seen from behind" in p and "slow spin on the spot." in p, p; n += 1
    assert "'slow spin on the spot' is not in the framing list" in notes and "far above or below" in notes, notes; n += 1
    assert labels == "full body back\nslow spin on the spot\nbird's eye view"; n += 1

    for bad in (("", "", "face set (6)", "", 6.0, 24), ("x", "", "custom", "  \n ", 6.0, 24),
                ("x", "", "nope", "", 6.0, 24), ("x", "", "custom", "\n".join(["a"] * 25), 30.0, 24),
                ("x", "", "face set (6)", "", 0.1, 24), ("x", "", "face set (6)", "", 5.0, 0)):
        try:
            m.build_look_sheet(*bad)
            raise SystemExit("bad input must raise: %r" % (bad[:3],))
        except ValueError:
            n += 1
    for names in m.PRESETS.values():
        for name in names:
            assert name in m.FRAMINGS, name
    n += 1
    out = m.SYH3LookSheetPrompt().run("her", "", "body set (6)", 8.0, 24)
    assert len(out) == 5 and out[3] == 6; n += 1
    return n
