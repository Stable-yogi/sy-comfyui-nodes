import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_video_size_presets as m


def _raises(*args):
    try:
        m.video_size(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.video_size("720p", "16:9", 16) == (1280, 720); n += 1
    assert m.video_size("720p", "9:16", 16) == (720, 1280); n += 1
    assert m.video_size("720p", "1:1", 16) == (720, 720); n += 1
    assert m.video_size("480p", "16:9", 16) == (848, 480); n += 1  # 853.3 rounds to 848
    assert m.video_size("480p", "16:9", 32) == (864, 480); n += 1
    assert m.video_size("480p", "1:1", 32) == (480, 480); n += 1
    assert m.video_size("1080p", "16:9", 16) == (1920, 1088); n += 1  # 1080 is not a multiple of 16
    assert m.video_size("1080p", "9:16", 32) == (1088, 1920); n += 1
    assert m.video_size("1080p", "1:1", 32) == (1088, 1088); n += 1
    for r in m.RESOLUTIONS:
        for a in m.ASPECTS:
            for mult in m.MULTIPLES:
                w, h = m.video_size(r, a, mult)
                assert w % mult == 0 and h % mult == 0 and w > 0 and h > 0
                n += 1
    for bad in (("4k", "16:9", 16), ("720p", "4:3", 16), ("720p", "16:9", 8), ("720p", "16:9", 0), (None, "1:1", 16)):
        assert _raises(*bad), bad
        n += 1
    assert m.SYVideoSizePresets().run("720p", "16:9", "16")[:2] == (1280, 720); n += 1
    return n + _extra(m)


def _extra(m):
    n = 0
    def ok(c):
        assert c
        return 1
    def rs(fn, *a, **k):
        try:
            fn(*a, **k)
        except ValueError as e:
            return str(e)
        return None
    n += ok(m.video_report('720p', '16:9', 16)[:2] == (1280, 720))
    n += ok(m.video_report('720p', '16:9', 16)[2] == '720p 16:9, multiple of 16: 1280x720 (0.92 MP, ratio 16:9, multiple of 16)')
    n += ok(m.video_report('1080p', '9:16', 32)[:2] == m.video_size('1080p', '9:16', 32))
    n += ok(rs(m.video_report, '4k', '16:9', 16) is not None)
    n += ok(len(m.SYVideoSizePresets().run('720p', '1:1', '32')) == 3)
    return n
