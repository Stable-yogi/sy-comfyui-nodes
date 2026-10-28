import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_time_code as m


def raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.frame_to_timecode(0, 24) == "00:00:00:00"; n += 1
    assert m.frame_to_timecode(23, 24) == "00:00:00:23"; n += 1
    assert m.frame_to_timecode(24, 24) == "00:00:01:00"; n += 1
    assert m.frame_to_timecode(84, 24) == "00:00:03:12"; n += 1
    assert m.frame_to_timecode(24 * 3600 + 24 * 60 + 25, 24) == "01:01:01:01"; n += 1
    assert m.frame_to_timecode(30, 29.97) == "00:00:01:00"; n += 1
    assert m.timecode_to_frame("00:00:03:12", 24) == 84; n += 1
    assert m.timecode_to_frame(" 01:01:01:01 ", 24) == 24 * 3600 + 24 * 60 + 25; n += 1
    for fr in (0, 1, 59, 1000, 123456):
        assert m.timecode_to_frame(m.frame_to_timecode(fr, 25), 25) == fr; n += 1
    c = m.convert("frame_to_timecode", 48, 24.0, "ignored")
    assert c == ("00:00:02:00", 2.0, 48); n += 1
    c = m.convert("timecode_to_frame", 0, 24.0, "00:00:02:12")
    assert c == ("00:00:02:12", 60 / 24.0, 60); n += 1
    assert raises(m.frame_to_timecode, -1, 24); n += 1
    assert raises(m.frame_to_timecode, 5, 0); n += 1
    assert raises(m.timecode_to_frame, "00:00:03", 24); n += 1
    assert raises(m.timecode_to_frame, "aa:bb:cc:dd", 24); n += 1
    assert raises(m.timecode_to_frame, "00:00:00:24", 24); n += 1  # frame part too big
    assert raises(m.timecode_to_frame, "00:60:00:00", 24); n += 1
    assert raises(m.timecode_to_frame, "00:00:-1:00", 24); n += 1
    assert raises(m.convert, "sideways", 1, 24.0, ""); n += 1
    assert m.SYTimeCode().run("frame_to_timecode", 24, 24.0, "")[0] == "00:00:01:00"; n += 1
    return n
