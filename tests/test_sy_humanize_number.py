import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_humanize_number as m


def run():
    n = 0
    h = m.humanize
    pairs = [
        ((0, "bytes", 1), "0 B"),
        ((512, "bytes", 1), "512 B"),
        ((1536, "bytes", 1), "1.5 KB"),
        ((1.5 * 1024 ** 3, "bytes", 1), "1.5 GB"),
        ((1023.99 * 1024, "bytes", 1), "1.0 MB"),
        ((2 * 1024 ** 4, "bytes", 0), "2 TB"),
        ((1e15, "bytes", 2), "909.49 TB"),
        ((-2048, "bytes", 1), "-2.0 KB"),
        ((0, "seconds", 1), "0.0 s"),
        ((5.5, "seconds", 1), "5.5 s"),
        ((59.96, "seconds", 1), "1 min"),
        ((90, "seconds", 0), "1 min 30 s"),
        ((3600, "seconds", 0), "1 h"),
        ((3725, "seconds", 0), "1 h 02 min 05 s"),
        ((3605, "seconds", 0), "1 h 00 min 05 s"),
        ((90061, "seconds", 0), "1 d 01 h 01 min 01 s"),
        ((-75, "seconds", 0), "-1 min 15 s"),
        ((12, "count", 1), "12"),
        ((999, "count", 1), "999"),
        ((12345, "count", 1), "12.3 k"),
        ((2500000, "count", 2), "2.50 M"),
        ((3e9, "count", 0), "3 B"),
        ((-1500, "count", 1), "-1.5 k"),
        ((-0.2, "count", 0), "0"),
    ]
    for args, want in pairs:
        assert h(*args) == want, (args, h(*args), want)
        n += 1
    for args, word in (((float("nan"),), "ordinary number"), (("x",), "ordinary number"), ((1, "mass"), "kind must be"),
                       ((1, "bytes", 9), "decimals must be"), ((1, "bytes", -1), "decimals must be")):
        try:
            h(*args)
            raise SystemExit("bad input must raise")
        except ValueError as e:
            assert word in str(e), str(e)
            n += 1
    assert m.SYHumanizeNumber().run(1536.0, "bytes", 1) == ("1.5 KB",); n += 1
    return n
