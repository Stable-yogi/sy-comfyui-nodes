import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_video_loop_frames as m

N = [0]


def ok(cond, msg="check failed"):
    N[0] += 1
    if not cond:
        raise AssertionError(msg)


def raises(fn, *args):
    N[0] += 1
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError for %r" % (args,))


def run():
    ok(m.loop_indices(3, 7, "repeat") == [0, 1, 2, 0, 1, 2, 0])
    ok(m.loop_indices(4, 10, "ping_pong") == [0, 1, 2, 3, 2, 1, 0, 1, 2, 3])
    ok(m.loop_indices(3, 2, "repeat") == [0, 1])
    ok(m.loop_indices(1, 4, "ping_pong") == [0, 0, 0, 0])
    ok(m.loop_indices(2, 5, "ping_pong") == [0, 1, 0, 1, 0])
    raises(m.loop_indices, 0, 5, "repeat")
    raises(m.loop_indices, 3, 0, "repeat")
    raises(m.loop_indices, 3, 5, "zigzag")
    ok(m.SYVideoLoopFrames.RETURN_TYPES[:2] == ("IMAGE", "INT"))
    # --- value pass A2: info line and the frame rule
    ok(m.loop_info(12, 81, "repeat") == "12 frames repeated to fill 81 frames: 6 full loops, the last loop stops after 9 of 12 frames, so the end may jump.")
    ok(m.loop_info(10, 30, "repeat") == "10 frames repeated to fill 30 frames: 3 full loops, the loops fit exactly.")
    ok(m.loop_info(10, 15, "repeat").startswith("10 frames repeated to fill 15 frames: 1 full loop, "))
    ok(m.loop_info(5, 20, "ping_pong") == "5 frames played forward and back to fill 20 frames.")
    ok(m.loop_info(1, 9, "repeat") == "1 frame held for 9 frames (a still).")
    ok(m.loop_info(20, 8, "repeat").startswith("20 frames cut to the first 8"))
    ok(m.loop_info(8, 8, "ping_pong").endswith("(the target equals the input)."))
    ok(m.SYVideoLoopFrames.RETURN_NAMES == ("images", "count", "info") and len(m.SYVideoLoopFrames.RETURN_TYPES) == 3)
    opt = m.SYVideoLoopFrames.INPUT_TYPES()["optional"]
    ok(opt["snap_to_rule"][1]["default"] is False and opt["frame_step"][1]["default"] == 4)
    return N[0]
