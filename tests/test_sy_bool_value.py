import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_bool_value as m


def run():
    assert m.bool_value(True) == (True, 1)
    assert m.bool_value(False) == (False, 0)
    assert m.SYBoolValue().run(True) == (True, 1)
    for bad in (1, 0, "yes", None):
        try:
            m.bool_value(bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYBoolValue.RETURN_TYPES == ("BOOLEAN", "INT")
    return 8
