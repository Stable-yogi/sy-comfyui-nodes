import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_date_parts as m


def run():
    assert m.date_parts("from_text", "2026-10-28") == (2026, 10, 28, "Wednesday", 301, 44)
    assert m.date_parts("from_text", "2024-02-29")[3] == "Thursday"
    assert m.date_parts("from_text", "2024-12-31")[4] == 366
    assert m.date_parts("from_text", "2026-01-01")[4] == 1
    assert m.date_parts("from_text", " 2026-01-04 ")[3] == "Sunday"
    assert m.date_parts("from_text", "2021-01-03")[5] == 53
    assert m.date_parts("now", "ignored", today=datetime.date(2025, 3, 9)) == (2025, 3, 9, "Sunday", 68, 10)
    assert m.date_parts("now", "")[0] >= 2026
    for bad in (("from_text", "28/10/2026"), ("from_text", "2026-13-01"), ("from_text", "2025-02-29"), ("from_text", ""), ("later", "2026-01-01")):
        try:
            m.date_parts(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            pass
    assert len(m.SYDateParts.RETURN_TYPES) == 6
    return 14  # checks
