import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_fade_mask_batch as m


def raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0

    def ok(cond, msg="check failed"):
        nonlocal n
        n += 1
        if not cond:
            raise SystemExit("fade mask batch: " + msg)

    for c in m.CURVES:
        ok(m.curve_value(0.0, c) == 0.0 and m.curve_value(1.0, c) == 1.0, "ends of " + c)
    ok(m.curve_value(0.5, "linear") == 0.5, "linear mid")
    ok(m.curve_value(0.5, "ease_in") == 0.25, "ease_in mid")
    ok(m.curve_value(0.5, "ease_out") == 0.75, "ease_out mid")
    ok(m.curve_value(0.5, "ease_in_out") == 0.5, "ease_in_out mid")
    ok(m.curve_value(2.0, "linear") == 1.0 and m.curve_value(-1, "linear") == 0.0, "clamps")
    ok(raises(m.curve_value, 0.5, "wobble"), "unknown curve")
    ok(m.frame_values(5, 0.0, 1.0) == [0.0, 0.25, 0.5, 0.75, 1.0], "linear values")
    ok(m.frame_values(3, 1.0, 0.0) == [1.0, 0.5, 0.0], "reverse values")
    ok(m.frame_values(1, 0.2, 0.8) == [0.8], "single frame is the end value")
    ok(len(m.frame_values(16, 0.0, 1.0, "ease_in_out")) == 16, "default count")
    ok(m.sweep_factor(0.0, 0.0) == 0.0 and m.sweep_factor(1.0, 1.0) == 1.0, "sweep ends")
    ok(m.sweep_factor(0.0, 1.0) == 1.0 and m.sweep_factor(1.0, 0.0) == 0.0, "sweep sides")
    row = m.sweep_row(9, 0.5)
    ok(all(row[i] >= row[i + 1] for i in range(8)), "edge falls from start to end side")
    ok(any(0.0 < v < 1.0 for v in row), "soft edge has in-between values")
    ok(m.sweep_row(9, 0.5, m.SOFT_EDGE, True) == row[::-1], "reverse flips")
    ok(m.sweep_row(5, 0.0) == [0.0] * 5 and m.sweep_row(5, 1.0) == [1.0] * 5, "row ends")
    ok(raises(m.check_args, 0, 4, 4, 0.0, 1.0, "whole"), "bad width")
    ok(raises(m.check_args, 4, 4, 0, 0.0, 1.0, "whole"), "bad frames")
    ok(raises(m.check_args, 4, 4, 4, -0.1, 1.0, "whole"), "bad start")
    ok(raises(m.check_args, 4, 4, 4, 0.0, 1.5, "whole"), "bad end")
    ok(raises(m.check_args, 4, 4, 4, 0.0, 1.0, "diagonal"), "bad direction")
    ok(m.NODE_DISPLAY_NAME_MAPPINGS["SYFadeMaskBatch"] == "Fade Mask Batch SY", "display name")
    ok(m.SYFadeMaskBatch.RETURN_TYPES == ("MASK", "STRING"), "return types")

    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        node = m.SYFadeMaskBatch()
        out, info = node.run(6, 4, 5, 0.0, 1.0, "linear", "whole")
        ok(tuple(out.shape) == (5, 4, 6), "whole shape")
        ok(float(out[0].max()) == 0.0 and float(out[-1].min()) == 1.0, "whole ends")
        ok(abs(float(out[2, 1, 1]) - 0.5) < 1e-6 and float(out[2].max()) == float(out[2].min()), "whole is even")
        for d in m.DIRECTIONS[1:]:
            o, _ = node.run(8, 6, 5, 0.0, 1.0, "linear", d)
            ok(tuple(o.shape) == (5, 6, 8), "shape " + d)
            ok(float(o[0].max()) == 0.0 and float(o[-1].min()) == 1.0, "ends " + d)
        o, _ = node.run(8, 6, 5, 0.0, 1.0, "linear", "left_to_right")
        ok(float(o[2, 0, 0]) > float(o[2, 0, 7]), "left_to_right reveals the left first")
        o, _ = node.run(8, 6, 5, 0.0, 1.0, "linear", "right_to_left")
        ok(float(o[2, 0, 7]) > float(o[2, 0, 0]), "right_to_left reveals the right first")
        o, _ = node.run(8, 6, 5, 0.0, 1.0, "linear", "top_to_bottom")
        ok(float(o[2, 0, 0]) > float(o[2, 5, 0]) and float(o[2, 3, 0]) == float(o[2, 3, 7]), "top_to_bottom rows")
        o, _ = node.run(8, 6, 5, 0.0, 1.0, "linear", "bottom_to_top")
        ok(float(o[2, 5, 0]) > float(o[2, 0, 0]), "bottom_to_top")
        o, info = node.run(4, 4, 3, 0.2, 0.6, "ease_in", "whole")
        ok(abs(float(o[0, 0, 0]) - 0.2) < 1e-6 and abs(float(o[2, 0, 0]) - 0.6) < 1e-6, "custom range")
        ok("3 masks" in info and "ease_in" in info, "info")
        try:
            node.run(4, 4, 3, 0.0, 1.0, "linear", "diagonal")
            ok(False, "should raise")
        except ValueError:
            ok(True)
    return n
