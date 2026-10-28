import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_dataset_pair_check as m


def run():
    ok, rep = m.pair_report(3, "a\nb\nc")
    assert ok and rep == "MATCH: 3 pictures and 3 captions."
    ok, rep = m.pair_report(3, "a\nb\nc\n")                                 # trailing new line is not a caption
    assert ok
    ok, rep = m.pair_report(3, "a\nb\nc\r\n")
    assert ok
    ok, rep = m.pair_report(3, "a\nb")
    assert not ok and "MISMATCH" in rep and "1 caption missing" in rep
    ok, rep = m.pair_report(5, "a\nb")
    assert not ok and "3 captions missing" in rep
    ok, rep = m.pair_report(2, "a\nb\nc\nd")
    assert not ok and "2 captions too many" in rep
    ok, rep = m.pair_report(2, "a\nb\nc")
    assert not ok and "1 caption too many" in rep
    ok, rep = m.pair_report(0, "")
    assert ok and "0 pictures and 0 captions" in rep
    ok, rep = m.pair_report(1, "")
    assert not ok and "1 caption missing" in rep and "1 pictures but 0 captions" in rep
    ok, rep = m.pair_report(3, "a\n\nc")                                    # blank middle line counts but is flagged
    assert ok and "WARNING" in rep and "line 2" in rep and "1 caption line is empty" in rep
    ok, rep = m.pair_report(2, "a\n\nc", True)                              # blank lines skipped
    assert ok and "WARNING" not in rep
    ok, rep = m.pair_report(3, "a\n  \n\nd")
    assert not ok and "2 caption lines are empty (line 2, 3)" in rep
    assert m.caption_lines("") == []
    assert m.caption_lines("a") == ["a"]
    assert m.caption_lines("a\n\n") == ["a", ""]
    assert m.caption_lines(None) == []
    try:
        m.pair_report(-1, "a")
        raise SystemExit("negative count must raise")
    except ValueError:
        pass

    class Fake:                                                             # stands in for a picture batch
        shape = (4, 8, 8, 3)

    assert m.SYDatasetPairCheck().run("a\nb\nc\nd", 0, False, images=Fake()) == (True, "MATCH: 4 pictures and 4 captions.")
    assert m.SYDatasetPairCheck().run("a\nb", 2, False)[0] is True
    return 22
