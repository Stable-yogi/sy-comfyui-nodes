import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_assert as m


def run():
    assert m.check_assert(True, "never shown") is True
    assert m.SYAssert().run(True, "x")[0] is True
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
    # new: off switch, info text
    assert m.check_assert(False, "x", enabled=False) is True
    assert m.check_assert(0, "x", False) is True                      # off means nothing is judged
    try:
        m.check_assert(False, "still stops", enabled=True)
        raise SystemExit("must raise")
    except ValueError as e:
        assert str(e) == "still stops"
    assert m.SYAssert().run(False, "x", False) == (True, "Check is switched off: nothing was tested.")
    assert m.SYAssert().run(True, "x") == (True, "Check passed: the value was yes.")
    assert m.assert_info(False) == "Check failed."
    assert m.SYAssert.RETURN_TYPES == ("BOOLEAN", "STRING") and len(m.SYAssert.RETURN_NAMES) == 2
    assert "enabled" in m.SYAssert.INPUT_TYPES()["optional"]
    return 23
