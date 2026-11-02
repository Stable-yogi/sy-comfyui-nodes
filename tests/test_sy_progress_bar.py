import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_progress_bar as m


def run():
    n = 0
    p = m.overall_percent
    assert p(10, 0) == 0.0 and p(10, 5) == 50.0 and p(0, 3) == 0.0; n += 1
    assert p(10, 5, 15, 30) == 55.0 and p(10, 5, 99, 30) == 60.0; n += 1  # a finished sub count never goes past the next node
    assert p(10, 10) == 99.0 and p(10, 10, 5, 5) == 99.0 and p(10, 99) == 99.0; n += 1
    assert p(10, 3, done=True) == 100.0; n += 1
    assert p(None, 3) == 0.0 and p("x", 3) == 0.0 and p(10, -4) == 0.0 and p(10, 1, 1, 0) == 10.0; n += 1
    assert m.format_elapsed(0) == "0:00" and m.format_elapsed(7999) == "0:07" and m.format_elapsed(65000) == "1:05"; n += 1
    assert m.format_elapsed(3723000) == "1:02:03" and m.format_elapsed(-5) == "0:00" and m.format_elapsed("x") == "0:00"; n += 1
    assert m.short_title("  Load   Checkpoint ") == "Load Checkpoint" and m.short_title("a" * 40, 10) == "a" * 9 + "…"; n += 1
    assert m.short_title(None) == "" and m.short_title("abc", 1) == "abc"; n += 1
    assert m.position_style("Bottom") == "bottom" and m.position_style("middle") == "top" and m.position_style(None) == "top"; n += 1
    cls = m.SYProgressBar
    assert cls().run() == () and cls.DESCRIPTION and m.NODE_DISPLAY_NAME_MAPPINGS["SYProgressBar"] == "Progress Bar SY"; n += 1
    return n
