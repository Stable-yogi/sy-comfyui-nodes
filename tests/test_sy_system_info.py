import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_system_info as m


def run():
    assert m.level_word(0) == "ok"
    assert m.level_word(84.9) == "ok"
    assert m.level_word(85) == "warn"
    assert m.level_word(94.9) == "warn"
    assert m.level_word(95) == "high"
    r = m.format_report(1000, 500, 2000, 100)
    lines = r.split("\n")
    assert len(lines) == 2
    assert "VRAM: 50% used" in lines[0] and "(ok)" in lines[0]
    assert "RAM: 95% used" in lines[1] and "(high)" in lines[1]
    assert "(warn)" in m.format_report(1000, 100, 1000, 900)
    assert "VRAM: unavailable" in m.format_report(-1, -1, 1000, 500)
    assert "RAM: unavailable" in m.format_report(1000, 500, -1, -1)
    out = m.SYSystemInfo().run()
    assert isinstance(out[0], str) and isinstance(out[1], int) and isinstance(out[2], int)
    v = m.SYSystemInfo.IS_CHANGED()
    assert v != v  # nan
    return 12  # checks
