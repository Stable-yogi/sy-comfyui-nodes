import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_size_presets as m


def run():
    n = 0
    assert len(m.PRESETS) == 20; n += 1
    assert m.preset_size("512x512 square") == (512, 512); n += 1
    assert m.preset_size("2048x1152 wide 16:9") == (2048, 1152); n += 1
    assert m.preset_size("832x1216 portrait") == (832, 1216); n += 1
    for name, (w, h) in m.PRESETS.items():
        assert name.startswith("%dx%d" % (w, h)), name  # label matches numbers
        assert w % 8 == 0 and h % 8 == 0, name
        n += 1
    for bad in ("", "nope", None):
        try:
            m.preset_size(bad)
            raise SystemExit("bad preset must raise")
        except ValueError:
            n += 1
    assert m.SYSizePresets().run("1024x1024 square") == (1024, 1024); n += 1
    return n
