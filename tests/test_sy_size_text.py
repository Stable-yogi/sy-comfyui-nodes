import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_size_text as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.size_text(0, "1024", 1) == "0 B"; n += 1
    assert m.size_text(1023, "1024", 1) == "1023 B"; n += 1
    assert m.size_text(1024, "1024", 1) == "1.0 KB"; n += 1
    assert m.size_text(1000, "1000", 1) == "1.0 KB"; n += 1
    assert m.size_text(999, "1000", 1) == "999 B"; n += 1
    assert m.size_text(5 * 1024 ** 3, "1024", 1) == "5.0 GB"; n += 1
    assert m.size_text(1048576, "1024", 1) == "1.0 MB"; n += 1
    assert m.size_text(1536, "1024", 1) == "1.5 KB"; n += 1
    assert m.size_text(1536, 1024, 0) in ("2 KB", "1 KB"); n += 1
    assert m.size_text(1500, "1000", 3) == "1.500 KB"; n += 1
    assert m.size_text(1024 ** 4, "1024", 2) == "1.00 TB"; n += 1
    assert m.size_text(1024 ** 5, "1024", 1) == "1.0 PB"; n += 1
    assert m.size_text(1024 ** 6, "1024", 1) == "1024.0 PB"; n += 1
    assert m.size_text(9007199254740991, "1024", 1).endswith(" PB"); n += 1
    assert m.size_text(1048575, "1024", 1) == "1.0 MB"; n += 1  # rounds up to the next unit
    assert m.size_text(1023, "1024", 4) == "1023 B"; n += 1
    msg = raises(m.size_text, -1, "1024", 1)
    assert msg and "bytes" in msg; n += 1
    msg = raises(m.size_text, 10, "512", 1)
    assert msg and "base" in msg; n += 1
    msg = raises(m.size_text, 10, "1024", 5)
    assert msg and "decimals" in msg; n += 1
    assert m.SYSizeText().run(2048, "1024", 1) == ("2.0 KB",); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSizeText"] == "Size Text SY"; n += 1
    assert m.SYSizeText.CATEGORY == "SY/Values"; n += 1
    return n
