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
    # added value: fit_size (snap and target megapixels)
    assert m.fit_size(1024, 1024) == (1024, 1024, "1024x1024; multiple of 64"); n += 1
    assert m.fit_size(1023, 777)[:2] == (1023, 777) and "not a multiple of 8" in m.fit_size(1023, 777)[2]; n += 1
    w, h, note = m.fit_size(1023, 777, "64")
    assert (w, h) == (1024, 768) and "snapped to a multiple of 64 (nearest)" in note and "multiple of 64" in note; n += 1
    assert m.fit_size(1023, 777, "64", "down")[:2] == (960, 768); n += 1
    assert m.fit_size(1023, 777, "64", "up")[:2] == (1024, 832); n += 1
    w, h, note = m.fit_size(1920, 1080, "off", "nearest", 1.0)
    assert abs(w * h - 1_000_000) / 1_000_000 < 0.01 and "scaled to about 1 MP" in note, (w, h); n += 1
    w, h, note = m.fit_size(1920, 1080, "16", "nearest", 1.0)
    assert (w, h) == (1328, 752) and w % 16 == 0 and h % 16 == 0, (w, h); n += 1
    w, h, note = m.fit_size(512, 512, "8", "nearest", 16.0)
    assert (w, h) == (4000, 4000) and "large" in note; n += 1
    assert m.fit_size(0, 0)[:2] == (0, 0); n += 1
    assert m.fit_size(10, 10, "64")[:2] == (64, 64); n += 1  # never below one step
    for bad in ((-1, 5), (5, 0, "64"), (0, 5, "off", "nearest", 1.0), (5, 5, "100"), (5, 5, "16", "sideways"),
                (5, 5, "off", "nearest", -1.0), (5, 5, "off", "nearest", float("nan"))):
        try:
            m.fit_size(*bad)
            raise SystemExit("must raise: %r" % (bad,))
        except ValueError:
            n += 1
    out = m.SYPixelCountInfo().run(1023, 777, "64")
    assert len(out) == 6 and out[3:5] == (1024, 768) and out[1] == 1023 * 777; n += 1
    assert m.SYPixelCountInfo().run(512, 512)[3:5] == (512, 512); n += 1
    spec = m.SYPixelCountInfo.INPUT_TYPES()
    assert list(spec["required"]) == ["width", "height"] and list(spec["optional"]) == ["snap_to", "snap_direction", "target_mp"]; n += 1
    assert m.SYPixelCountInfo.RETURN_NAMES[:3] == ("megapixels", "pixels", "report") and len(m.SYPixelCountInfo.RETURN_TYPES) == 6; n += 1
    return n
