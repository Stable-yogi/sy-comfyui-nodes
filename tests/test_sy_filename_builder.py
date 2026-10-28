import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_filename_builder as m

NOW = datetime(2026, 10, 28, 14, 5, 9)


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.build_filename("shot_{date}_{counter}", 0, 3, "", NOW) == "shot_2026-10-28_00003"; n += 1
    assert m.build_filename("{time}-{seed}", 99, 0, "png", NOW) == "140509-99.png"; n += 1
    assert m.build_filename("plain", 0, 1, ".TXT", NOW) == "plain.txt"; n += 1
    for bad in ("", "a/b", "a\\b", "{x}", "{counter}{counter}", "C:\\x"):
        assert raises(m.build_filename, bad, 0, 1, "", NOW), bad; n += 1
    assert raises(m.build_filename, "a", 0, -1, "", NOW); n += 1
    assert raises(m.build_filename, "a", 0, 1, "p/g", NOW); n += 1
    assert m.SYFilenameBuilder.RETURN_TYPES == ("STRING",); n += 1
    return n
