import os
import sys
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import _sy_safe_paths as m

NOW = datetime(2026, 10, 28, 14, 5, 9)


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "out")
        os.makedirs(os.path.join(base, "a", "b"))
        real = os.path.realpath(base)
        # good paths
        assert m.safe_join(base, "") == real; n += 1
        assert m.safe_join(base, None) == real; n += 1
        assert m.safe_join(base, "a/b") == os.path.join(real, "a", "b"); n += 1
        assert m.safe_join(base, "a\\b") == os.path.join(real, "a", "b"); n += 1
        assert m.safe_join(base, "./a//b/") == os.path.join(real, "a", "b"); n += 1
        assert m.safe_join(base, "new/folder") == os.path.join(real, "new", "folder"); n += 1
        # attack strings
        for bad in ("../x", "..", "..\\x", "C:\\x", "c:/x", "D:x", "/etc/x", "\\etc\\x", "a/../../x",
                    "a/b/../../../x", "\\\\host\\share", "//host/share", "a:b", "x\x00y", "a/..\\..\\x"):
            assert raises(m.safe_join, base, bad), "should refuse %r" % bad; n += 1
        # symlink escape
        outside = os.path.join(tmp, "outside")
        os.makedirs(outside)
        link = os.path.join(base, "link")
        made = False
        try:
            os.symlink(outside, link, target_is_directory=True)
            made = True
        except (OSError, NotImplementedError, AttributeError):
            made = False
        if made:
            assert raises(m.safe_join, base, "link"); n += 1
            assert raises(m.safe_join, base, "link/deeper"); n += 1
        # list_files
        for name in ("B.png", "a.JPG", "c.txt", "d.png"):
            open(os.path.join(base, "a", name), "w").close()
        assert m.list_files(os.path.join(base, "a")) == ["a.JPG", "B.png", "c.txt", "d.png"]; n += 1
        assert m.list_files(os.path.join(base, "a"), (".png",)) == ["B.png", "d.png"]; n += 1
        assert m.list_files(os.path.join(base, "a"), m.IMAGE_EXTENSIONS) == ["a.JPG", "B.png", "d.png"]; n += 1
        assert m.list_files(os.path.join(base, "nope")) == []; n += 1
        assert "b" not in m.list_files(os.path.join(base, "a")); n += 1
    # filename tokens
    assert m.expand_pattern("{date}_{time}_{seed}", 42, NOW) == "2026-10-28_140509_42"; n += 1
    assert m.expand_pattern("x_{counter}", 1, NOW) == "x_{counter}"; n += 1
    assert m.expand_pattern("x_{counter}", 1, NOW, counter=7) == "x_00007"; n += 1
    for bad in ("{nope}", "a{b", "a}b", "{counter}{counter}", "{ date }"):
        assert raises(m.expand_pattern, bad, 0, NOW), bad; n += 1
    # check_filename
    assert m.check_filename("ok name.png") == "ok name.png"; n += 1
    for bad in ("", "  ", "a/b", "a\\b", "a:b", "a?b", "a*b", "a|b", "<x>", "end.", " lead", "CON", "nul.txt", "x" * 200, "..", "a\x01b"):
        assert raises(m.check_filename, bad), repr(bad); n += 1
    # extensions
    assert m.clean_extension("PNG") == ".png"; n += 1
    assert m.clean_extension("") == ""; n += 1
    assert raises(m.clean_extension, ".p/g"); n += 1
    assert m.parse_extensions("png, .JPG ;txt png") == (".png", ".jpg", ".txt"); n += 1
    assert m.parse_extensions("", default=()) == (); n += 1
    assert m.parse_extensions("") == m.IMAGE_EXTENSIONS; n += 1
    # counter logic
    assert m.plan_names([], "img_{counter}", ".png", 3, 0, NOW) == ["img_00001.png", "img_00002.png", "img_00003.png"]; n += 1
    ex = ["img_00001.png", "img_00007.png", "other.png", "IMG_00003.PNG"]
    assert m.plan_names(ex, "img_{counter}", ".png", 2, 0, NOW) == ["img_00008.png", "img_00009.png"]; n += 1
    assert m.plan_names(["img_00004.txt"], "img_{counter}", ".png", 1, 0, NOW, companion=".txt") == ["img_00005.png"]; n += 1
    assert m.plan_names(["img_00004.txt"], "img_{counter}", ".png", 1, 0, NOW) == ["img_00001.png"]; n += 1
    assert m.plan_names([], "{date}_s{seed}_{counter}", ".jpg", 1, 5, NOW) == ["2026-10-28_s5_00001.jpg"]; n += 1
    assert m.plan_names(["a_1_00002.png"], "a_{seed}_{counter}", ".png", 1, 1, NOW) == ["a_1_00003.png"]; n += 1
    assert m.plan_names(["a_2_00009.png"], "a_{seed}_{counter}", ".png", 1, 1, NOW) == ["a_1_00001.png"]; n += 1
    # no counter token: plain name, then suffixes
    assert m.plan_names([], "pic", ".png", 1, 0, NOW) == ["pic.png"]; n += 1
    assert m.plan_names(["pic.png"], "pic", ".png", 2, 0, NOW) == ["pic_00001.png", "pic_00002.png"]; n += 1
    assert m.plan_names([], "pic", ".png", 2, 0, NOW) == ["pic.png", "pic_00001.png"]; n += 1
    assert m.plan_names(["PIC.PNG"], "pic", ".png", 1, 0, NOW) == ["pic_00001.png"]; n += 1
    assert m.plan_names(["pic.txt"], "pic", ".png", 1, 0, NOW, companion=".txt") == ["pic_00001.png"]; n += 1
    for bad_args in (([], "", ".png", 1), ([], "a/b", ".png", 1), ([], "a{x}", ".png", 1), ([], "a", ".png", 0)):
        assert raises(m.plan_names, *bad_args); n += 1
    # pick_index
    assert m.pick_index(5, 7) == 2; n += 1
    assert raises(m.pick_index, 0, 1); n += 1
    return n
