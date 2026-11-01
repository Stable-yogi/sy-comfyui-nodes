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
    assert m.SYSizePresets().run("1024x1024 square")[:2] == (1024, 1024); n += 1
    return n + _extra(m)


def _extra(m):
    n = 0
    def ok(c):
        assert c
        return 1
    def rs(fn, *a, **k):
        try:
            fn(*a, **k)
        except ValueError as e:
            return str(e)
        return None
    n += ok(m.preset_size('1216x832 landscape', True) == (832, 1216))
    n += ok(m.preset_size('1216x832 landscape') == (1216, 832))
    n += ok(m.preset_size('1344x768 wide') == (1344, 768))
    n += ok(len(m.PRESETS) == 20 and len(m.MORE_PRESETS) == 5)
    n += ok('unknown size preset' in rs(m.preset_size, 'nope'))
    n += ok(m.preset_report('1024x1024 square')[2] == '1024x1024 square: 1024x1024 (1.05 MP, ratio 1:1, multiple of 64)')
    n += ok(', swapped' in m.preset_report('512x768 portrait', True)[2])
    n += ok(m.SYSizePresets().run('928x1664 portrait', True)[:2] == (1664, 928))
    n += ok(list(m.SYSizePresets.INPUT_TYPES()['required']['preset'][0])[-1] == '928x1664 portrait')
    return n
