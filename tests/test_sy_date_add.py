import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_date_add as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    D = datetime.date
    a = m.add_to_date
    assert a(2026, 1, 31, 7, "days") == D(2026, 2, 7); n += 1
    assert a(2026, 1, 31, -31, "days") == D(2025, 12, 31); n += 1
    assert a(2026, 1, 31, 2, "weeks") == D(2026, 2, 14); n += 1
    assert a(2027, 1, 31, 1, "months") == D(2027, 2, 28); n += 1
    assert a(2028, 1, 31, 1, "months") == D(2028, 2, 29); n += 1
    assert a(2026, 12, 15, 2, "months") == D(2027, 2, 15); n += 1
    assert a(2026, 3, 31, -1, "months") == D(2026, 2, 28); n += 1
    assert a(2026, 1, 15, -13, "months") == D(2024, 12, 15); n += 1
    assert a(2024, 2, 29, 1, "years") == D(2025, 2, 28); n += 1
    assert a(2024, 2, 29, 4, "years") == D(2028, 2, 29); n += 1
    # business days: 2026-01-30 is a Friday
    assert D(2026, 1, 30).weekday() == 4; n += 1
    assert a(2026, 1, 30, 1, "business days") == D(2026, 2, 2); n += 1
    assert a(2026, 1, 30, 5, "business days") == D(2026, 2, 6); n += 1
    assert a(2026, 1, 30, 12, "business days") == D(2026, 2, 17); n += 1
    assert a(2026, 2, 2, -1, "business days") == D(2026, 1, 30); n += 1
    assert a(2026, 1, 31, 1, "business days") == D(2026, 2, 2); n += 1   # start on Saturday
    assert a(2026, 1, 30, 0, "business days") == D(2026, 1, 30); n += 1
    # whole function
    assert m.date_add("2026-01-31", 7, "days", "YYYY-MM-DD") == ("2026-02-07", "Saturday", 38, 7); n += 1
    assert m.date_add("31/01/2027", 1, "months", "DD/MM/YYYY") == ("28/02/2027", "Sunday", 59, 28); n += 1
    assert m.date_add("2026-01-31", 0, "days", "D Month YYYY") == ("31 January 2026", "Saturday", 31, 0); n += 1
    assert m.date_add("2026-03-01", -1, "days", "weekday, D Month YYYY")[0] == "Saturday, 28 February 2026"; n += 1
    assert m.date_add("2026-03-01", -1, "days", "YYYY-MM-DD")[3] == -1; n += 1
    assert m.date_add("2028-12-31", 0, "days", "YYYY-MM-DD")[2] == 366; n += 1
    # today (pinned for the test through the today argument)
    assert m.date_add("today", 1, "days", "YYYY-MM-DD", D(2026, 5, 5))[0] == "2026-05-06"; n += 1
    assert m.parse_date(" TODAY ") == D.today(); n += 1
    # big amounts and limits
    assert a(2026, 1, 1, 100000, "days") == D(2026, 1, 1) + datetime.timedelta(days=100000); n += 1
    assert a(2026, 1, 1, 100000, "business days") > D(2026, 1, 1); n += 1
    assert "1 to 9999" in _raises(a, 9999, 12, 31, 1, "days"); n += 1
    assert "1 to 9999" in _raises(a, 9999, 1, 1, 100000, "years"); n += 1
    # refusals
    assert "real date" in _raises(m.parse_date, "2026-02-30"); n += 1
    assert "real date" in _raises(m.parse_date, "31.01.2026"); n += 1
    assert "real date" in _raises(m.parse_date, "26-01-31"); n += 1
    assert "empty" in _raises(m.parse_date, "  "); n += 1
    assert "unit" in _raises(a, 2026, 1, 1, 1, "decades"); n += 1
    assert "output_format" in _raises(m.date_add, "2026-01-01", 1, "days", "US"); n += 1
    node = m.SYDateAdd()
    assert node.run("2026-01-31", 7, "days", "YYYY-MM-DD") == ("2026-02-07", "Saturday", 38, 7); n += 1
    assert m.SYDateAdd.IS_CHANGED("2026-01-01", 1, "days", "YYYY-MM-DD") == ""; n += 1
    return n
