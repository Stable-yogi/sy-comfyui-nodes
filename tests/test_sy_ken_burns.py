import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_ken_burns as m


def run():
    n = 0

    def ok(cond, msg="check failed"):
        nonlocal n
        n += 1
        if not cond:
            raise SystemExit(msg)

    b = m.ken_burns_boxes(640, 480, 10, 1.0, 1.0, 0.0, 0.0, "linear")
    ok(len(b) == 10)
    ok(all(box == (0.0, 0.0, 640.0, 480.0) for box in b), "zoom 1 shows the whole picture")
    for ease in m.EASES:
        for px, py in ((0, 0), (1, 1), (-1, -1), (1, -1)):
            boxes = m.ken_burns_boxes(640, 480, 25, 1.0, 3.0, px, py, ease)
            ok(all(0 <= x0 < x1 <= 640 and 0 <= y0 < y1 <= 480 for x0, y0, x1, y1 in boxes),
               "box must stay inside the picture (%s %s %s)" % (ease, px, py))
    z = m.ken_burns_boxes(100, 100, 5, 1.0, 2.0, 0.0, 0.0, "linear")
    ok(abs((z[-1][2] - z[-1][0]) - 50.0) < 1e-9, "zoom 2 gives half-width box")
    ok(abs((z[0][2] - z[0][0]) - 100.0) < 1e-9)
    pan = m.ken_burns_boxes(100, 100, 5, 2.0, 2.0, 1.0, 0.0, "linear")
    ok(pan[0][0] == 0.0 and pan[-1][2] == 100.0, "pan 1 goes from left edge to right edge")
    ok(pan[0][1] == pan[-1][1] == 25.0, "no vertical pan stays centred")
    for bad in ((0, 10, 5, 1, 1, 0, 0, "linear"), (10, 10, 1, 1, 1, 0, 0, "linear"), (10, 10, 5, 0.5, 1, 0, 0, "linear"),
                (10, 10, 5, 1, 1, 2, 0, "linear"), (10, 10, 5, 1, 1, 0, 0, "bounce")):
        try:
            m.ken_burns_boxes(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    ok(m.SYKenBurns.RETURN_TYPES == ("IMAGE",))
    return n
