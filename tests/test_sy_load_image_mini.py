import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_load_image_mini as m
from _sy_common import safe_join


def run():
    names = ["b.PNG", "a.jpg", "notes.txt", "C.webp", "d.bmp", "e.JPEG", "a.png", "clip.mp4"]
    got = m.list_image_files(names)
    assert got == ["a.jpg", "a.png", "b.PNG", "C.webp", "d.bmp", "e.JPEG"], got
    assert m.list_image_files([]) == []
    assert m.normalize_filename("  pic.png  ") == "pic.png"
    assert m.normalize_filename("sub\\pic.png") == "sub/pic.png"
    assert m.normalize_filename("./pic.png [input]") == "pic.png"
    try:
        m.normalize_filename("   ")
        raise SystemExit("empty name must raise")
    except ValueError:
        pass
    base = os.path.dirname(os.path.abspath(__file__))
    assert safe_join(base, m.normalize_filename("x.png")).startswith(os.path.realpath(base))
    try:
        safe_join(base, m.normalize_filename("../outside.png"))
        raise SystemExit("path escape must raise")
    except ValueError:
        pass
    assert m.SYLoadImageMini.RETURN_TYPES == ("IMAGE", "MASK", "INT", "INT", "STRING")
    assert m.SYLoadImageMini.RETURN_NAMES[-1] == "info"
    n = 11
    # --- case-insensitive match and suggestions
    files = ["Photo.PNG", "sky.jpg", "sky_2.jpg", "cat.webp"]
    assert m.match_name("Photo.PNG", files) == ("Photo.PNG", [])
    assert m.match_name("photo.png", files) == ("Photo.PNG", [])
    assert m.match_name("./SKY.JPG [input]", files) == ("sky.jpg", [])
    found, close = m.match_name("sky.png", files)
    assert found == "" and close == ["sky.jpg", "sky_2.jpg"]
    assert m.match_name("dog.png", files) == ("", [])
    n += 5
    # --- crop to a multiple
    assert m.crop_to_multiple_box(1023, 770, 1) == (0, 0, 1023, 770)
    assert m.crop_to_multiple_box(1023, 770, 8) == (3, 1, 1016, 768)
    assert m.crop_to_multiple_box(1024, 768, 64) == (0, 0, 1024, 768)
    for bad in ((10, 10, 0), (10, 100, 64)):
        try:
            m.crop_to_multiple_box(*bad)
            raise SystemExit("must raise")
        except ValueError:
            pass
    n += 5
    # --- megapixel cap
    assert m.max_mp_size(4000, 3000, 0) == (4000, 3000)
    assert m.max_mp_size(1000, 1000, 2.0) == (1000, 1000)
    w, h = m.max_mp_size(4000, 3000, 1.0)
    assert w * h <= 1000000 and abs(w / h - 4 / 3.0) < 0.01
    try:
        m.max_mp_size(10, 10, -1)
        raise SystemExit("must raise")
    except ValueError:
        pass
    n += 4
    # --- info line
    t = m.load_info("a.png", 1023, 770, 1016, 768, False, ["trimmed to a multiple of 8"])
    assert "a.png: 1023x770 -> 1016x768" in t and "no transparency" in t and "trimmed" in t and t.endswith(".")
    t = m.load_info("b.png", 64, 64, 64, 64, True, [])
    assert "->" not in t and "has transparency" in t
    n += 4
    return n
