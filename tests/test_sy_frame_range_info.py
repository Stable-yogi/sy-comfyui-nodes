import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_frame_range_info as m

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
    ok(m.range_info(0, 8, 2) == ("0, 2, 4, 6, 8", 5, 8))
    ok(m.range_info(0, 7, 2) == ("0, 2, 4, 6", 4, 6))
    ok(m.range_info(5, 5, 1) == ("5", 1, 5))
    ok(m.range_info(10, 4, 3) == ("10, 7, 4", 3, 4))
    ok(m.frame_range(0, 3, 1) == [0, 1, 2, 3])
    raises(m.frame_range, 0, 10, 0)
    raises(m.frame_range, 0, 10000000, 1)
    ok(m.SYFrameRangeInfo().run(1, 3, 1)[:3] == ("1, 2, 3", 3, 3))
    ok(len(m.SYFrameRangeInfo().run(1, 3, 1)) == 5)
    # added value: fps, 4n+1 rule, info
    r = m.plan_range(0, 80, 1, 16)
    ok(r[1] == 81 and r[2] == 80 and r[3] == 5.062 and "81 frames" in r[4] and "5.06 s at 16 fps" in r[4] and "not 4n+1" not in r[4])
    r = m.plan_range(0, 79, 1)
    ok(r[1] == 80 and r[3] == 0.0 and "not 4n+1" in r[4])
    r = m.plan_range(0, 79, 1, 0, "4n+1 trim")
    ok(r[1] == 77 and r[2] == 76 and "Changed 80 frames to 77" in r[4] and "not 4n+1" not in r[4])
    r = m.plan_range(0, 79, 1, 0, "4n+1 extend")
    ok(r[1] == 81 and r[2] == 80)
    r = m.plan_range(0, 80, 2, 0, "4n+1 extend")  # 41 frames is 4n+1 already
    ok(r[1] == 41 and r[2] == 80 and "Changed" not in r[4])
    r = m.plan_range(10, 4, 1, 0, "4n+1 trim")  # counts down: 7 frames -> 5
    ok(r[1] == 5 and r[2] == 6)
    raises(m.plan_range, 3, 0, 1, 0, "4n+1 extend")  # 4 frames -> 5 would need -1
    raises(m.plan_range, 0, 10, 1, -1)
    raises(m.plan_range, 0, 10, 1, float("nan"))
    raises(m.plan_range, 0, 10, 1, 0, "sideways")
    raises(m.plan_range, 0, 10, 0)
    ok(m.SYFrameRangeInfo().run(0, 79, 1, 8, "4n+1 extend")[1] == 81)
    ok(m.SYFrameRangeInfo().run(0, 8, 2)[:3] == ("0, 2, 4, 6, 8", 5, 8))
    spec = m.SYFrameRangeInfo.INPUT_TYPES()
    ok(list(spec["required"]) == ["start", "end", "step"] and list(spec["optional"]) == ["fps", "frame_rule"])
    ok(m.SYFrameRangeInfo.RETURN_NAMES[:3] == ("list", "count", "last") and len(m.SYFrameRangeInfo.RETURN_TYPES) == 5)
    return N[0]
