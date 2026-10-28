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
    assert m.SYLoadImageMini.RETURN_TYPES == ("IMAGE", "MASK", "INT", "INT")
    return 10  # checks
