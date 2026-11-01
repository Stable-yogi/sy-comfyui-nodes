import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_exists as m


def run():
    n = 0
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "refs"))
        with open(os.path.join(d, "refs", "hero.png"), "wb") as f:
            f.write(b"x")
        assert m.check_exists(d, "refs/hero.png") == (True, "refs/hero.png"); n += 1
        assert m.check_exists(d, "refs\\hero.png") == (True, "refs/hero.png"); n += 1
        assert m.check_exists(d, "refs/none.png") == (False, "refs/none.png"); n += 1
        assert m.check_exists(d, "refs")[0] is False; n += 1
        assert m.check_exists(d, "") == (False, ""); n += 1
        assert m.check_exists(d, "   ") == (False, ""); n += 1
        for bad in ("../x.png", "refs/../../x.png", "/etc/x", "\\x.png", "C:/x.png", "C:x.png", "a\x00b"):
            try:
                m.check_exists(d, bad)
                raise SystemExit("bad name must raise: %r" % bad)
            except ValueError as e:
                assert "stay inside" in str(e)
            n += 1
        # added value: find_file
        r = m.find_file(d, "refs/hero.png")
        assert r[:3] == (True, "refs/hero.png", "refs/hero.png") and "Found refs/hero.png in the input folder, 1 bytes" in r[3]; n += 1
        case_fs = os.path.isfile(os.path.join(d, "refs", "HERO.PNG"))  # Windows ignores case already
        assert m.find_file(d, "refs/Hero.PNG")[0] is case_fs; n += 1
        r = m.find_file(d, "refs/Hero.PNG", "input", True)
        assert r[0] is True and r[1] == "refs/Hero.PNG" and r[2].lower() == "refs/hero.png"; n += 1
        assert m.find_file(d, "refs/hero")[0] is False; n += 1
        r = m.find_file(d, "refs/hero", "input", False, True)
        assert r[0] is True and r[2] == "refs/hero.png"; n += 1
        r = m.find_file(d, "refs/HERO", "input", True, True)
        assert r[0] is True and r[2] == "refs/hero.png"; n += 1  # name has no ending, so the ending is tried
        r = m.find_file(d, "refs/heroo.png")
        assert r[0] is False and r[2] == "" and "Close names in that folder: hero.png" in r[3]; n += 1
        r = m.find_file(d, "refs/zzzzzz.png")
        assert r[0] is False and "No similar file names" in r[3] and "(1 files there)" in r[3]; n += 1
        r = m.find_file(d, "nope/x.png")
        assert r[0] is False and "does not exist" in r[3]; n += 1
        r = m.find_file(d, "  ")
        assert r == (False, "", "", "No file name given, so nothing to look for."); n += 1
        with open(os.path.join(d, "big.png"), "wb") as f:
            f.write(b"x" * 2048)
        assert "2.0 KB" in m.find_file(d, "big.png")[3]; n += 1
        for bad in ("../x.png", "/etc/x", "C:/x.png"):
            try:
                m.find_file(d, bad, "input", True, True)
                raise SystemExit("must raise")
            except ValueError as e:
                assert "stay inside" in str(e)
            n += 1
    assert m.SYImageExists.RETURN_TYPES == ("BOOLEAN", "STRING", "STRING", "STRING"); n += 1
    assert m.SYImageExists.RETURN_NAMES == ("exists", "full_name", "found_name", "info"); n += 1
    spec = m.SYImageExists.INPUT_TYPES()
    assert list(spec["required"]) == ["folder", "filename"] and list(spec["optional"]) == ["ignore_case", "try_extensions"]; n += 1
    v2 = m.SYImageExists.IS_CHANGED("input", "a", ignore_case=True)
    assert v2 != v2; n += 1
    v = m.SYImageExists.IS_CHANGED("input", "a")
    assert v != v; n += 1
    return n
