import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_folder_image_count as m
import _sy_safe_paths as sp


def run():
    n = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name in ("a.png", "b.JPG", "c.jpeg", "d.webp", "e.txt", "f.gif", "g.bmp", "h.tif"):
            open(os.path.join(tmp, name), "w").close()
        os.makedirs(os.path.join(tmp, "sub.png"))
        assert len(sp.list_files(tmp, m.IMAGE_EXTENSIONS)) == 7; n += 1
        assert len(sp.list_files(os.path.join(tmp, "missing"), m.IMAGE_EXTENSIONS)) == 0; n += 1
        # added value: extensions, subfolders, if_missing, info
        c, last, info = m.count_info(tmp, "input", "")
        assert (c, last) == (7, 6) and "7 files in input" in info and "0 to 6" in info and "png 1" in info; n += 1
        c, last, info = m.count_info(tmp, "input", "", "png, webp")
        assert c == 2 and "png 1, webp 1" in info; n += 1
        c, last, info = m.count_info(tmp, "input", "", "txt")
        assert (c, last) == (1, 0); n += 1
        c, last, info = m.count_info(tmp, "input", "", "mp4")
        assert (c, last) == (0, -1) and "No files with the endings .mp4" in info; n += 1
        os.makedirs(os.path.join(tmp, "deep", "er"))
        open(os.path.join(tmp, "deep", "x.png"), "w").close()
        open(os.path.join(tmp, "deep", "er", "y.png"), "w").close()
        assert m.count_info(tmp, "input", "")[0] == 7; n += 1
        c, last, info = m.count_info(tmp, "input", "", "", True)
        assert c == 9 and "including subfolders" in info; n += 1
        assert m.count_info(tmp, "input", "", "png", True)[0] == 3; n += 1
        gone = os.path.join(tmp, "missing")
        c, last, info = m.count_info(gone, "input", "missing")
        assert (c, last) == (0, -1) and "does not exist" in info and "input/missing" in info; n += 1
        try:
            m.count_info(gone, "input", "missing", "", False, "error")
            raise SystemExit("must raise")
        except ValueError as e:
            assert "'missing'" in str(e) or "missing" in str(e)
            n += 1
        for bad in (("x", "input", "", "", False, "sometimes"),):
            try:
                m.count_info(tmp, *bad[1:])
                raise SystemExit("must raise")
            except ValueError:
                n += 1
        try:
            m.count_info(tmp, "input", "", "p/g")
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    assert m.SYFolderImageCount.RETURN_TYPES == ("INT", "INT", "STRING"); n += 1
    assert m.SYFolderImageCount.RETURN_NAMES == ("count", "last_index", "info"); n += 1
    spec = m.SYFolderImageCount.INPUT_TYPES()
    assert list(spec["required"]) == ["root", "subfolder"] and list(spec["optional"]) == ["extensions", "include_subfolders", "if_missing"]; n += 1
    v = m.SYFolderImageCount.IS_CHANGED("input", "", extensions="png")
    assert v != v; n += 1
    return n
