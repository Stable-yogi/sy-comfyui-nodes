import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_aspect_from_image as m


def run():
    n = 0
    assert m.aspect_from_size(1920, 1080)[0] == "16:9"
    n += 1
    assert m.aspect_from_size(1024, 1024)[0] == "1:1"
    n += 1
    assert m.aspect_from_size(1080, 1920)[0] == "9:16"
    n += 1
    assert m.aspect_from_size(1024, 768)[0] == "4:3"
    n += 1
    assert m.aspect_from_size(2560, 1080)[0] == "21:9"  # 64:27 is not small, nearest common wins
    n += 1
    assert m.aspect_from_size(1000, 1001)[0] == "1:1"
    n += 1
    assert m.aspect_from_size(1, 1)[0] == "1:1"
    n += 1
    r, f = m.aspect_from_size(1536, 1024)
    assert r == "3:2" and abs(f - 1.5) < 1e-9
    n += 1
    assert abs(m.aspect_from_size(1920, 1080)[1] - 16 / 9) < 1e-9
    n += 1
    assert m.aspect_from_size(1088, 1920)[0] == "9:16"
    n += 1
    for bad in ((0, 10), (10, 0), (-5, 5)):
        try:
            m.aspect_from_size(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError:
            pass
    n += 1
    assert m.SYAspectFromSize().run(1600, 900)[:2] == ("16:9", 1600 / 900)
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
    n += ok(m.aspect_report(1600, 900)[2] == 'landscape')
    n += ok(m.aspect_report(900, 1600)[2] == 'portrait')
    n += ok(m.aspect_report(512, 512)[2] == 'square')
    n += ok(m.aspect_report(1600, 900)[3] == '1600x900 is 16:9, landscape, 1.44 megapixels')
    n += ok('closest to' in m.aspect_report(1013, 677)[3] and 'exact shape' in m.aspect_report(1013, 677)[3])
    n += ok(m.aspect_report(1600, 900)[:2] == m.aspect_from_size(1600, 900))
    n += ok(rs(m.aspect_report, 0, 5) is not None)
    n += ok(len(m.SYAspectFromSize().run(10, 10)) == 4)
    return n
