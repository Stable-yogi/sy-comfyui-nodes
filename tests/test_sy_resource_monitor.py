import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_resource_monitor as m
import _sy_resource_api as api


def run():
    n = 0
    assert m.percent(50, 200) == 25.0 and m.percent(1, 3) == 33.3 and m.percent(5, 0) == 0.0 and m.percent("x", 10) == 0.0; n += 1
    assert m.percent(300, 100) == 100.0 and m.percent(-5, 100) == 0.0 and m.percent(None, None) == 0.0; n += 1
    assert m.level(10) == "ok" and m.level(70) == "warn" and m.level(89.9) == "warn" and m.level(90) == "hot" and m.level("x") == "ok"; n += 1
    assert m.temp_level(60) == "ok" and m.temp_level(75) == "warn" and m.temp_level(85) == "hot" and m.temp_level(None) == "ok"; n += 1
    assert m.format_gb(1024 ** 3) == "1.0 GB" and m.format_gb(-5) == "0.0 GB" and m.format_gb("x") == "0.0 GB"; n += 1
    assert m.clean_interval(0.1) == 0.5 and m.clean_interval(99) == 10.0 and m.clean_interval("x") == 1.0 and m.clean_interval(float("nan")) == 1.0; n += 1
    s = m.build_snapshot(12.34, 8 * 1024 ** 3, 32 * 1024 ** 3, [
        {"name": "RTX", "util": 40, "vram_used": 12 * 1024 ** 3, "vram_total": 24 * 1024 ** 3, "temp": 61},
        {"name": "Other", "util": None, "vram_used": None, "vram_total": 0, "temp": None},
    ])
    assert s["cpu"] == 12.3 and s["ram"]["percent"] == 25.0 and len(s["gpus"]) == 2; n += 1
    assert s["gpus"][0]["vram"]["percent"] == 50.0 and s["gpus"][0]["temp"] == 61; n += 1
    assert s["gpus"][1]["util"] is None and s["gpus"][1]["vram"] is None and s["gpus"][1]["temp"] is None; n += 1
    e = m.build_snapshot(None, 0, 0, None)
    assert e == {"cpu": None, "ram": None, "gpus": []}; n += 1
    assert m.build_snapshot(250, 1, 2, [])["cpu"] == 100.0; n += 1
    # the real reader never crashes, with or without psutil and a GPU
    snap = api.read_snapshot()
    assert set(snap) == {"cpu", "ram", "gpus"} and isinstance(snap["gpus"], list); n += 1
    assert api.register_routes() in (True, False); n += 1
    cls = m.SYResourceMonitor
    assert cls().run() == () and cls.DESCRIPTION and m.NODE_DISPLAY_NAME_MAPPINGS["SYResourceMonitor"] == "Resource Monitor SY"; n += 1
    return n
