import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_frame_number_overlay as m


def run():
    n = 0

    def ok(cond, msg="check failed"):
        nonlocal n
        n += 1
        if not cond:
            raise SystemExit(msg)

    ok(m.label_text(12, 24.0, 0, "frame and time") == "f 0012 | 0.50 s")
    ok(m.label_text(12, 24.0, 0, "frame") == "f 0012")
    ok(m.label_text(12, 24.0, 0, "time") == "0.50 s")
    ok(m.label_text(0, 24.0, 100, "frame") == "f 0100", "start number is added")
    ok(m.label_text(48, 24.0, 0, "time") == "2.00 s")
    for bad in ((1, 24.0, 0, "words"), (1, 0.0, 0, "frame")):
        try:
            m.label_text(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    ok(m.corner_origin("top left", 100, 50, 20, 10) == (4, 4))
    ok(m.corner_origin("bottom right", 100, 50, 20, 10) == (76, 36))
    ok(m.corner_origin("top right", 100, 50, 20, 10) == (76, 4))
    ok(m.corner_origin("bottom left", 100, 50, 20, 10) == (4, 36))
    ok(m.corner_origin("top left", 10, 10, 50, 50)[0] >= 0, "label bigger than picture never goes negative")
    try:
        m.corner_origin("middle", 10, 10, 5, 5)
        raise SystemExit("bad corner must raise")
    except ValueError:
        n += 1
    ok(m.SYFrameNumberOverlay.RETURN_TYPES == ("IMAGE",))
    return n
