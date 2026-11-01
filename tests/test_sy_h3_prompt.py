import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_prompt as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.picture_numbers("Picture 1 hugs picture2, PICTURE 2 again") == [1, 2]; n += 1
    assert m.picture_numbers("") == [] and m.picture_numbers(None) == []; n += 1
    assert m.connected_slots([True, False, True, False]) == [1, 3]; n += 1
    assert m.slot_to_picture([1, 3]) == {1: 1, 3: 2}; n += 1
    # picture checks both ways
    w = m.check_pictures("Picture 1 meets Picture 3", 2)
    assert any("Picture 3" in x for x in w) and any("Picture 2" in x for x in w); n += 1
    assert m.check_pictures("Picture 1 and Picture 2", 2) == []; n += 1
    assert m.check_pictures("no pictures here", 0) == []; n += 1
    assert any("never mentions" in x for x in m.check_pictures("nothing", 1)); n += 1
    # picture lines
    lines, warns = m.picture_lines(["the hero.", "", "a dog", ""], [1, 3])
    assert lines == ["Picture 1 is the hero.", "Picture 2 is a dog."] and any("Picture 2" in x for x in warns); n += 1
    lines, warns = m.picture_lines(["", "a cat", "", ""], [1])
    assert lines == [] and any("ref_note_2" in x for x in warns); n += 1
    # time codes
    assert m.time_code_ends("0-4s: a\n4-9s: b\nbad line") == [4.0, 9.0]; n += 1
    assert m.check_time_codes("0-4s: a\n4-9s: b", 5.0) and not m.check_time_codes("0-4s: a", 5.0); n += 1
    # length
    f, real, lines = m.plan_length(0, 24, 0)
    assert f == 124 and abs(real - 124 / 24.0) < 0.01; n += 1
    f, real, lines = m.plan_length(0, 24, 100)
    assert f == 107 and "acting video" in lines[0]; n += 1   # 100 frames wanted -> next valid 17*6+5 = 107
    f, real, lines = m.plan_length(2.0, 24, 200)
    assert f == 56 and any("WARNING" in x and "200" in x for x in lines); n += 1
    assert raises(m.plan_length, -1, 24, 0) and raises(m.plan_length, 1, 0, 0); n += 1
    assert "All checks passed" in m.make_info(["x"]) and "All checks" not in m.make_info(["WARNING: x"]); n += 1
    # node as a whole (no pictures needed)
    node = m.SYH3Prompt()
    assert raises(node.run, "", "", ""); n += 1
    try:
        import torch
    except ImportError:
        return n
    p, frames, refs, info = node.run("film", "A room. Picture 1 stands.", "Picture 1 waves.", time_codes="0-8s: waves")
    assert "Style: film" in p and frames == 124 and "WARNING" in info; n += 1
    a = torch.rand(1, 32, 48, 3)
    b = torch.rand(2, 16, 16, 4)
    p, frames, refs, info = node.run("film", "A room.", "Picture 1 meets Picture 2.", ref_image_1=a, ref_image_3=b,
                                     ref_note_1="a girl", ref_note_3="a dog", acting_video=torch.rand(48, 8, 8, 3))
    assert tuple(refs.shape) == (2, 32, 48, 3); n += 1
    assert "Picture 1 is a girl." in p and "Picture 2 is a dog." in p; n += 1
    assert frames == 56 and "48 frames" in info and "WARNING" not in info; n += 1
    p, frames, refs, info = node.run("a", "b", "c")
    assert tuple(refs.shape) == (1, 64, 64, 3) and float(refs.sum()) == 0.0; n += 1
    return n
