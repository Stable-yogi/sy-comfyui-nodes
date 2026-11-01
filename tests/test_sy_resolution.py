import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_resolution as m


def run():
    n = 0
    w, h = m.compute_size("Custom", "1:1", "landscape", 1.0, 64)
    assert (w, h) == (1024, 1024), (w, h)
    n += 1
    for mult in (8, 16, 32, 64):
        for aspect in m.ASPECTS:
            w, h = m.compute_size("Custom", aspect, "landscape", 1.0, mult)
            assert w % mult == 0 and h % mult == 0 and w >= mult and h >= mult, (mult, aspect, w, h)
    n += 1
    w, h = m.compute_size("Custom", "16:9", "landscape", 1.0, 16)
    assert w > h and abs(w * h - 1e6) / 1e6 < 0.05, (w, h)
    n += 1
    pw, ph = m.compute_size("Custom", "16:9", "portrait", 1.0, 16)
    assert (pw, ph) == (h, w)
    n += 1
    # a portrait aspect with landscape orientation is the same as the landscape aspect
    assert m.compute_size("Custom", "9:16", "landscape", 1.0, 16) == (w, h)
    n += 1
    w, h = m.compute_size("Custom", "21:9", "landscape", 1.0, 16)
    assert abs(w / h - 21 / 9) < 0.08 and abs(w * h - 1e6) / 1e6 < 0.05, (w, h)
    n += 1
    w, h = m.compute_size("Custom", "1:1", "landscape", 0.1, 64)
    assert w >= 64 and h >= 64 and w % 64 == 0 and h % 64 == 0, (w, h)
    n += 1
    w, h = m.compute_size("Custom", "21:9", "landscape", 0.1, 64)  # tiny MP: never below the multiple
    assert w >= 64 and h >= 64, (w, h)
    n += 1
    w, h = m.compute_size("MOSS-Image (multiple of 32)", "3:2", "landscape", 9.0, 8)  # preset ignores inputs
    assert w % 32 == 0 and h % 32 == 0 and abs(w * h - 1e6) / 1e6 < 0.06, (w, h)
    n += 1
    w, h = m.compute_size("Qwen Image 2.1 (1.5 MP)", "1:1", "landscape", 0.1, 8)
    assert abs(w * h - 1.5e6) / 1.5e6 < 0.03, (w, h)
    n += 1
    w, h = m.compute_size("Custom", "1:1", "landscape", 16.0, 64)
    assert abs(w * h - 16e6) / 16e6 < 0.02, (w, h)
    n += 1
    for bad in (("Nope", "1:1", "landscape", 1.0, 16), ("Custom", "5:7", "landscape", 1.0, 16),
                ("Custom", "1:1", "sideways", 1.0, 16), ("Custom", "1:1", "landscape", 0, 16)):
        try:
            m.compute_size(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError:
            pass
    n += 1
    assert m.SYResolution().run("Custom", "4:3", "landscape", 1.0, 16)[:2] == m.compute_size("Custom", "4:3", "landscape", 1.0, 16)
    n += 1
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
    n += ok(m.compute_size('Custom', '16:9', 'landscape', 2.0, 16, 0.0) == m.compute_size('Custom', '16:9', 'landscape', 2.0, 16))
    n += ok((lambda s: s[0] * s[1] <= 1_000_000)(m.compute_size('Custom', '16:9', 'landscape', 2.0, 16, 1.0)))
    n += ok((lambda s: s[0] * s[1] <= 1_000_000 and s[1] > s[0])(m.compute_size('Custom', '9:16', 'portrait', 3.0, 8, 1.0)))
    n += ok((lambda s: s[0] % 16 == 0 and s[1] % 16 == 0)(m.compute_size('Custom', '3:2', 'landscape', 4.0, 16, 1.0)))
    n += ok(m.compute_size('Custom', '1:1', 'landscape', 0.5, 16, 4.0) == m.compute_size('Custom', '1:1', 'landscape', 0.5, 16))
    n += ok(m.compute_size('SDXL (1 MP, multiple of 64)', '1:1', 'landscape', 9, 8) == (1024, 1024))
    n += ok(all(x % 64 == 0 for x in m.compute_size('SD 1.5 (0.26 MP, multiple of 64)', '3:2', 'landscape', 9, 8)))
    n += ok('too small' in rs(m.compute_size, 'Custom', '1:1', 'landscape', 1.0, 64, 0.001))
    n += ok(rs(m.compute_size, 'Custom', '1:1', 'landscape', 1.0, 64, -1) is not None)
    n += ok('lowered to stay under 1 MP' in m.resolution_report('Custom', '16:9', 'landscape', 2.0, 16, 1.0)[2])
    n += ok(m.resolution_report('Krea 2 (1 MP)', '1:1', 'landscape', 1.0, 16)[2].startswith('Krea 2 (1 MP), 1:1 landscape: 1024x1024 ('))
    n += ok(list(m.PRESETS)[:5] == ['Krea 2 (1 MP)', 'Qwen Image 2.1 (1.5 MP)', 'MOSS-Image (multiple of 32)', 'Flux (1 MP)', 'Custom'])
    for mp, mult in (('Krea 2 (1 MP)', 16), ('Flux (1 MP)', 16), ('MOSS-Image (multiple of 32)', 32)):
        sq = m.compute_size(mp, '1:1', 'landscape', 1.0, 16)
        n += ok(sq[0] == sq[1] and sq[0] % mult == 0)
    n += ok(m.compute_size('Krea 2 (1 MP)', '1:1', 'landscape', 1.0, 16) == (1024, 1024))
    n += ok(m.compute_size('Qwen Image 2.1 (1.5 MP)', '1:1', 'landscape', 1.0, 16) == (1232, 1232))
    n += ok(m.compute_size('Krea 2 (1 MP)', '16:9', 'landscape', 1.0, 16) == (1328, 752))
    return n
