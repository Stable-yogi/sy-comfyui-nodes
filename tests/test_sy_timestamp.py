import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_timestamp as m


def run():
    t = 1700000000  # 2023-11-14 22:13:20 UTC
    assert m.format_time(t, "date", True) == "2023-11-14"
    assert m.format_time(t, "time", True) == "22-13-20"
    assert m.format_time(t, "date_time", True) == "2023-11-14_22-13-20"
    assert m.format_time(t, "compact", True) == "20231114221320"
    assert m.format_time(t, "unix", True) == "1700000000"
    assert m.format_time(t + 0.9, "unix", False) == "1700000000"
    assert len(m.format_time(t, "compact", False)) == 14
    try:
        m.format_time(t, "bogus")
        raise SystemExit("bogus format must raise")
    except ValueError:
        pass
    out = m.SYTimestamp().run("compact", True)
    assert len(out) == 1 and len(out[0]) == 14 and out[0].isdigit()
    assert m.SYTimestamp.CATEGORY == "SY/Utility"
    return 10
