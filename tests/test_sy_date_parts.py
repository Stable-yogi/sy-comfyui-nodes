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
    assert len(m.SYDateParts.RETURN_TYPES) == 10
    n = 14
    # added value: other input styles, offset, format, extras
    assert m.date_parts("from_text", "20261028") == (2026, 10, 28, "Wednesday", 301, 44); n += 1
    assert m.date_parts("from_text", "2026/10/28")[2] == 28 and m.date_parts("from_text", "2026.10.28")[2] == 28; n += 1
    assert m.date_parts("from_text", "2026-10-28", offset_days=-28)[:3] == (2026, 9, 30); n += 1
    assert m.date_parts("from_text", "2026-12-31", offset_days=1)[:3] == (2027, 1, 1); n += 1
    assert m.date_parts("from_text", "2024-03-01", offset_days=-1)[:3] == (2024, 2, 29); n += 1
    assert m.date_parts("now", "", today=datetime.date(2025, 3, 9), offset_days=1)[3] == "Monday"; n += 1
    d = datetime.date(2026, 3, 5)
    assert m.format_date(d) == "2026-03-05" and m.format_date(d, "YYYYMMDD") == "20260305"; n += 1
    assert m.format_date(d, "DD.MM.YYYY") == "05.03.2026" and m.format_date(d, "DD-MM-YYYY") == "05-03-2026"; n += 1
    assert m.format_date(d, "YYYY/MM/DD") == "2026/03/05" and m.format_date(d, "Month D, YYYY") == "March 5, 2026"; n += 1
    text, month, weekend, info = m.date_extras("from_text", "2026-10-31", None, 0, "DD.MM.YYYY")
    assert (text, month, weekend) == ("31.10.2026", "October", True) and "Saturday" in info and "61 days left in 2026" in info; n += 1
    assert m.date_extras("from_text", "2026-10-30")[2] is False; n += 1
    assert "Moved +2 days" in m.date_extras("from_text", "2026-10-28", None, 2)[3]; n += 1
    assert m.date_extras("from_text", "2026-10-28", None, 3)[2] is True; n += 1  # Saturday
    for bad in (("from_text", "2026-10-28", None, 40000), ("from_text", "9999-12-31", None, 1)):
        try:
            m.date_parts(*bad)
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    try:
        m.format_date(d, "bad")
        raise SystemExit("must raise")
    except ValueError:
        n += 1
    out = m.SYDateParts().run("from_text", "2026-10-28", 1, "YYYYMMDD")
    assert len(out) == 10 and out[:3] == (2026, 10, 29) and out[6] == "20261029" and out[7] == "October" and out[8] is False; n += 1
    assert len(m.SYDateParts().run("from_text", "2026-10-28")) == 10; n += 1
    assert m.SYDateParts.IS_CHANGED("now", "x", 3, "YYYYMMDD") != m.SYDateParts.IS_CHANGED("now", "x", 3, "YYYYMMDD"); n += 1  # nan
    assert m.SYDateParts.IS_CHANGED("from_text", "x", 3, "YYYYMMDD") == m.SYDateParts.IS_CHANGED("from_text", "x", 3, "YYYYMMDD"); n += 1
    assert m.SYDateParts.IS_CHANGED("from_text", "x") != m.SYDateParts.IS_CHANGED("from_text", "x", 1); n += 1
    spec = m.SYDateParts.INPUT_TYPES()
    assert list(spec["required"]) == ["mode", "date_text"] and list(spec["optional"]) == ["offset_days", "date_format"]; n += 1
    return n
