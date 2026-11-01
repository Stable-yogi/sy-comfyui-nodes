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
    # added value: plan_listing
    ents = [("b.png", 20.0, 2048), ("A.png", 10.0, 100), ("c.txt", 30.0, 5), ("sub/d.png", 5.0, 1000)]
    names, total, info = m.plan_listing(ents)
    assert names == ["A.png", "b.png", "c.txt", "sub/d.png"] and total == 4 and "4 files" in info and "sorted by name" in info and "png 3, txt 1" in info; n += 1
    assert m.plan_listing(ents, "newest")[0][0] == "c.txt"; n += 1
    assert m.plan_listing(ents, "oldest")[0][0] == "sub/d.png"; n += 1
    assert m.plan_listing(ents, "largest")[0][0] == "b.png"; n += 1
    assert m.plan_listing(ents, "smallest")[0][0] == "c.txt"; n += 1
    names, total, info = m.plan_listing(ents, "name", "PNG a")
    assert names == ["A.png"] and total == 1 and "1 of 4 files in the folder matched" in info; n += 1
    assert m.plan_listing(ents, "name", "zzz") == ([], 0, "0 files, 0 B, sorted by name. Filter: zzz (0 of 4 files in the folder matched)."); n += 1
    assert m.plan_listing(ents, "name", "", 100, "error", "shots")[0][0] == "shots/A.png"; n += 1
    assert m.plan_listing(ents, "name", "", 100, "error", "shots/")[0][0] == "shots/A.png"; n += 1
    names, total, info = m.plan_listing(ents, "name", "", 2, "truncate")
    assert names == ["A.png", "b.png"] and total == 4 and "2 of 4 files" in info and "if_too_many is truncate" in info; n += 1
    for bad in ((ents, "name", "", 2, "error"), (ents, "sideways"), (ents, "name", "", 5, "maybe")):
        try:
            m.plan_listing(*bad)
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    try:
        m.plan_listing(ents, "name", "", 2)
    except ValueError as e:
        assert "if_too_many to truncate" in str(e)
        n += 1
    assert m.plan_listing([], "name")[2].startswith("0 files"); n += 1
    assert m.SYListFolderFiles.RETURN_TYPES == ("STRING", "INT", "STRING"); n += 1
    assert m.SYListFolderFiles.RETURN_NAMES == ("files", "count", "info"); n += 1
    spec = m.SYListFolderFiles.INPUT_TYPES()
    assert list(spec["required"]) == ["root", "subfolder", "extensions"]; n += 1
    assert list(spec["optional"]) == ["sort_by", "include_subfolders", "contains", "with_subfolder", "if_missing", "if_too_many"]; n += 1
    v = m.SYListFolderFiles.IS_CHANGED("input", "", "", sort_by="newest")
    assert v != v; n += 1
    return n
