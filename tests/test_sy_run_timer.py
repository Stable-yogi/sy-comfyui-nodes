import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_run_timer as m


def run():
    assert m.format_elapsed(65.3) == "1m 05.3s"
    assert m.format_elapsed(5.0) == "5.0s"
    assert m.format_elapsed(0) == "0.0s"
    assert m.format_elapsed(-4) == "0.0s"
    assert m.format_elapsed(3600) == "60m 00.0s"
    assert m.elapsed_for("t1", now=100.0) == 0.0
    assert m.elapsed_for("t1", now=102.5) == 2.5
    assert m.elapsed_for("t1", reset=True, now=110.0) == 0.0
    assert m.elapsed_for("t2", now=111.0) == 0.0
    assert m.elapsed_for("t1", now=111.0) == 1.0
    node = m.SYRunTimer()
    v, e = node.run("hello", False, "n1")
    assert v == "hello" and e >= 0.0
    v2, e2 = node.run("x", False, "n1")
    assert e2 >= e
    assert (m.ANY != "IMAGE") is False and m.ANY == "*"
    cid = m.SYRunTimer.IS_CHANGED()
    assert cid != cid  # NaN
    return 15
