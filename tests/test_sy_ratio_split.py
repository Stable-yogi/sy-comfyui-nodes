import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_ratio_split as m


def run():
    assert m.ratio_split(100, "1:2:1") == (25.0, 50.0, 25.0, 0.0, "25, 50, 25")
    assert m.ratio_split(100, "1:3")[:4] == (25.0, 75.0, 0.0, 0.0)
    assert m.ratio_split(10, "5")[:4] == (10.0, 0.0, 0.0, 0.0)
    assert m.ratio_split(8, "1:1:1:1")[:4] == (2.0, 2.0, 2.0, 2.0)
    assert m.ratio_split(9, " 1 : 2 ")[:2] == (3.0, 6.0)
    assert m.ratio_split(10, "0:1")[:2] == (0.0, 10.0)
    assert m.ratio_split(-10, "1:1")[:2] == (-5.0, -5.0)
    assert m.parse_ratios("0.5:1.5") == [0.5, 1.5]
    assert m.ratio_split(100, "1:1")[4] == "50, 50"
    for bad in ("", "a:b", "1:-1", "0:0", "1:1:1:1:1", "1::2", "nan:1"):
        try:
            m.ratio_split(10, bad)
            raise SystemExit("bad ratios must raise: %r" % bad)
        except ValueError:
            pass
    assert m.SYRatioSplit.RETURN_TYPES == ("FLOAT", "FLOAT", "FLOAT", "FLOAT", "STRING")
    return 17  # checks
