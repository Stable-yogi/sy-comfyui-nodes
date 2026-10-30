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
    assert m.SYImageExists.RETURN_TYPES == ("BOOLEAN", "STRING"); n += 1
    v = m.SYImageExists.IS_CHANGED("input", "a")
    assert v != v; n += 1
    return n
