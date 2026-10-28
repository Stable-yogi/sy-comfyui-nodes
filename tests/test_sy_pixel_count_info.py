import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_pixel_count_info as m


def run():
    n = 0
    mp, px, text = m.pixel_info(1000, 1000)
    assert mp == 1.0 and px == 1_000_000 and "1:1" in text and "square" in text; n += 1
    mp, px, text = m.pixel_info(1920, 1080)
    assert px == 2_073_600 and abs(mp - 2.0736) < 1e-9 and "16:9" in text and "landscape" in text; n += 1
    mp, px, text = m.pixel_info(1080, 1920)
    assert "9:16" in text and "portrait" in text; n += 1
    mp, px, text = m.pixel_info(0, 500)
    assert mp == 0.0 and px == 0 and "empty" in text; n += 1
    mp, px, text = m.pixel_info(0, 0)
    assert px == 0 and isinstance(text, str); n += 1
    mp, px, text = m.pixel_info(1_000_000, 1_000_000)
    assert px == 10 ** 12 and mp == 1_000_000.0; n += 1  # huge
    mp, px, text = m.pixel_info(1023, 777)  # non-multiples
    assert px == 1023 * 777 and "1023x777" in text; n += 1
    for bad in ((-1, 5), (5, -1)):
        try:
            m.pixel_info(*bad)
            raise SystemExit("negative must raise")
        except ValueError:
            n += 1
    assert m.SYPixelCountInfo().run(512, 512)[1] == 262144; n += 1
    return n
