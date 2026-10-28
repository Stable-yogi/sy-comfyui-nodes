import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_aspect_bucket as m


def bad(fn, *args):
    try:
        fn(*args)
    except ValueError as e:
        return str(e)
    raise SystemExit("must raise: %r" % (args,))


def run():
    assert m.parse_buckets("1:1, 4:3") == [(1, 1), (4, 3), (3, 4)]
    assert m.parse_buckets("1:1, 4:3", False) == [(1, 1), (4, 3)]
    assert m.parse_buckets("16/9\n3:2") == [(16, 9), (9, 16), (3, 2), (2, 3)]
    assert m.parse_buckets("1:1, 1:1, 4:3, 3:4") == [(1, 1), (4, 3), (3, 4)]      # no repeats
    assert "not a ratio" in bad(m.parse_buckets, "banana")
    assert "not a ratio" in bad(m.parse_buckets, "16:0")
    assert "not a ratio" in bad(m.parse_buckets, "1:2:3")
    assert "not a ratio" in bad(m.parse_buckets, "1.5:1")
    assert "empty" in bad(m.parse_buckets, " , ")
    # sizes
    assert m.bucket_size(1, 1, 1024) == (1024, 1024)
    assert m.bucket_size(16, 9, 1024) == (1344, 768)
    assert m.bucket_size(9, 16, 1024) == (768, 1344)
    assert m.bucket_size(4, 3, 1024) == (1152, 896)
    assert m.bucket_size(3, 2, 1024) == (1280, 832)
    assert m.bucket_size(1, 1, 512) == (512, 512)
    assert m.bucket_size(1, 1, 1000, 8) == (1000, 1000)
    assert m.bucket_size(100, 1, 64) == (640, 64)                                   # never below one step
    for ratio in ((16, 9), (21, 9), (5, 4), (2, 3)):
        w, h = m.bucket_size(ratio[0], ratio[1], 1024)
        assert w % 64 == 0 and h % 64 == 0
    # choosing
    assert m.pick_bucket(1024, 1024) == (1024, 1024, "1:1")
    assert m.pick_bucket(1920, 1080) == (1344, 768, "16:9")
    assert m.pick_bucket(1080, 1920) == (768, 1344, "9:16")
    assert m.pick_bucket(1000, 800) == (1152, 896, "4:3")
    assert m.pick_bucket(800, 1000) == (896, 1152, "3:4")
    assert m.pick_bucket(1500, 1000) == (1280, 832, "3:2")
    assert m.pick_bucket(1000, 1010) == (1024, 1024, "1:1")
    assert m.pick_bucket(4000, 1000)[2] == "16:9"                                    # widest one wins
    assert m.pick_bucket(1080, 1920, "1:1, 4:3, 3:2, 16:9", 1024, 64, False)[2] == "1:1"   # no flips: 1:1 is nearest
    assert m.pick_bucket(512, 512, "1:1, 16:9", 512, 64) == (512, 512, "1:1")
    # log scale: 2:1 and 1:2 are equally far from 1:1, the first listed wins a tie
    assert m.pick_bucket(1, 1, "2:1", 1024, 64, True)[2] == "2:1"
    assert "at least 1" in bad(m.pick_bucket, 0, 100)
    assert "at least 1" in bad(m.pick_bucket, 100, -3)
    assert "multiple" in bad(m.pick_bucket, 100, 100, "1:1", 1024, 0)
    assert "target" in bad(m.pick_bucket, 100, 100, "1:1", 32, 64)
    assert "not a ratio" in bad(m.pick_bucket, 100, 100, "x")
    assert m.SYAspectBucket().run(1920, 1080, "1:1, 4:3, 3:2, 16:9", True, 1024, 64) == (1344, 768, "16:9")
    return 36
