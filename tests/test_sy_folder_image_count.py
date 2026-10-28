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
    assert m.SYFolderImageCount.RETURN_TYPES == ("INT",); n += 1
    return n
