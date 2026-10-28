import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_list_folder_files as m
import _sy_safe_paths as sp


def run():
    n = 0
    assert m.list_text(["a.png", "b.txt"]) == ("a.png\nb.txt", 2); n += 1
    assert m.list_text([]) == ("", 0); n += 1
    try:
        m.list_text(["x"] * 4, limit=3)
        raise SystemExit("too many files must raise")
    except ValueError:
        n += 1
    with tempfile.TemporaryDirectory() as tmp:
        for name in ("one.png", "Two.PNG", "three.txt", "four.jpg"):
            open(os.path.join(tmp, name), "w").close()
        os.makedirs(os.path.join(tmp, "dir.png"))
        exts = sp.parse_extensions("png", default=()) or None
        assert m.list_text(sp.list_files(tmp, exts)) == ("one.png\nTwo.PNG", 2); n += 1
        exts = sp.parse_extensions("", default=()) or None
        assert m.list_text(sp.list_files(tmp, exts))[1] == 4; n += 1
        exts = sp.parse_extensions(".txt, jpg", default=()) or None
        assert m.list_text(sp.list_files(tmp, exts)) == ("four.jpg\nthree.txt", 2); n += 1
    assert m.SYListFolderFiles.RETURN_TYPES == ("STRING", "INT"); n += 1
    return n
