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
    # --- value pass A2: memory need check
    n = 12
    ok, t = m.check_needs(8192, 32768, 6, 16)
    assert ok is True and "VRAM ok: 8.0 GB free, 6 GB needed." in t and "RAM ok" in t; n += 1
    ok, t = m.check_needs(4096, 32768, 12, 0)
    assert ok is False and t.startswith("Not enough VRAM: 4.0 GB free, 12 GB needed.") and "Not enough RAM" not in t; n += 1
    ok, t = m.check_needs(1024, 1024, 4, 4)
    assert ok is False and "VRAM" in t and "RAM" in t; n += 1
    assert m.check_needs(-1, 100, 8, 0) == (True, "VRAM could not be read, so it was not checked."); n += 1
    assert m.check_needs(100, 100) == (True, "No memory need was given, so nothing was checked."); n += 1
    try:
        m.check_needs(100, 100, -1, 0)
        raise SystemExit("negative need must raise")
    except ValueError:
        n += 1
    assert m.check_needs(1024, 0, 1, 0)[0] is True; n += 1  # exactly enough
    out = m.SYSystemInfo().run()
    assert len(out) == len(m.SYSystemInfo.RETURN_TYPES) == len(m.SYSystemInfo.RETURN_NAMES) == 8 and out[5] is True; n += 1
    if m.read_vram_mb()[1] < 0:  # no GPU here: a stop request cannot fire for an unknown value
        assert m.SYSystemInfo().run(need_vram_gb=1000, stop_if_short=True)[5] is True; n += 1
    return n
