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
    assert m.SYAspectFromSize().run(1600, 900) == ("16:9", 1600 / 900)
    n += 1
    return n
