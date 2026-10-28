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
    ok(m.SYVideoLoopFrames.RETURN_TYPES == ("IMAGE", "INT"))
    return N[0]
