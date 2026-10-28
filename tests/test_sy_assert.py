import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_assert as m


def run():
    assert m.check_assert(True, "never shown") is True
    assert m.SYAssert().run(True, "x") == (True,)
    try:
        m.check_assert(False, "Width must be 1024")
        raise SystemExit("must raise")
    except ValueError as e:
        assert str(e) == "Width must be 1024"
    for msg in ("", "   ", None):
        try:
            m.check_assert(False, msg)
            raise SystemExit("must raise")
        except ValueError as e:
            assert str(e) == m.DEFAULT_MESSAGE
    try:
        m.check_assert(False, "x" * 900)
    except ValueError as e:
        assert len(str(e)) == m.MAX_MESSAGE
    try:
        m.SYAssert().run(False, "stop here")
        raise SystemExit("node must raise")
    except ValueError as e:
        assert str(e) == "stop here"
    for bad in (0, "yes", None):
        try:
            m.check_assert(bad, "m")
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert "yes or no" in str(e)
    assert m.SYAssert.OUTPUT_NODE is True
    return 14
