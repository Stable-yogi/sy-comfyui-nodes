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
    assert len(out[0]) == 14 and out[0].isdigit()
    assert m.SYTimestamp.CATEGORY == "SY/Utility"
    # --- value pass A2: custom pattern, zone text, extra outputs
    n = 10
    assert m.format_custom(t, "%Y%m%d_%H%M", True) == "20231114_2213"; n += 1
    assert m.format_custom(t, "%A %d %B %Y", True) == "Tuesday 14 November 2023"; n += 1
    assert m.format_custom(t, "%H:%M:%S", True) == "22-13-20"; n += 1  # the colon is not allowed in a file name
    assert m.format_custom(t, "%H:%M", True, False) == "22:13"; n += 1
    assert m.format_custom(t, "100%% %y", True) == "100% 23"; n += 1
    assert m.format_custom(t, "run %j", True) == "run 318"; n += 1
    for bad in ("", "  ", "%Q", "%", "%-d", "%f"):
        try:
            m.format_custom(t, bad, True)
            raise SystemExit("bad pattern must raise: %r" % bad)
        except ValueError:
            n += 1
    assert m.zone_text(t, True) == "UTC"; n += 1
    z = m.zone_text(t, False)
    assert z == "local time" or (z.startswith("UTC") and len(z) == 9); n += 1
    o = m.SYTimestamp().run("compact", True, "%Y", True)
    assert len(o) == len(m.SYTimestamp.RETURN_TYPES) == 3 and len(o[0]) == 4 and o[1] > 1700000000 and "custom pattern, UTC" in o[2]; n += 1
    o = m.SYTimestamp().run("date", True)
    assert len(o[0]) == 10 and o[2].endswith("(format date, UTC)"); n += 1
    assert m.SYTimestamp.RETURN_NAMES == ("timestamp", "unix_seconds", "info"); n += 1
    return n
